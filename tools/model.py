"""
Load the repo into memory and answer one question honestly: what is deployable?

Every other tool goes through here, so the rule that sandbox/ can never ship is
enforced in exactly one place — discovery only ever walks courses/. There is no
flag, env var or CLI option that widens it.
"""

from __future__ import annotations

import dataclasses
import json
import pathlib
import sys

try:
    import yaml
except ImportError:                                            # pragma: no cover
    sys.exit("pyyaml is required:  pip install -r tools/requirements.txt")

REPO = pathlib.Path(__file__).resolve().parent.parent
COURSES = REPO / "courses"
SCHEMAS = REPO / "schemas"

# Cover images. grape decides the real format from the bytes, but catching it here
# turns a 400 in a deploy log into a line in a PR — and the schema check below is
# skipped when jsonschema is absent, so these rules run unconditionally instead.
THUMBNAIL_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
THUMBNAIL_MAX_BYTES = 2 * 1024 * 1024


class ValidationError(Exception):
    """A problem a human has to fix. Carries the offending path."""

    def __init__(self, where: pathlib.Path | str, message: str):
        self.where = where
        self.message = message
        super().__init__(f"{_rel(where)}: {message}")


def _rel(path) -> str:
    try:
        return str(pathlib.Path(path).resolve().relative_to(REPO))
    except (ValueError, OSError):
        return str(path)


# --------------------------------------------------------------------------- #
# documents
# --------------------------------------------------------------------------- #

def load_yaml(path: pathlib.Path) -> dict:
    if not path.is_file():
        raise ValidationError(path, "missing")
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValidationError(path, f"not valid YAML — {exc}") from exc
    if not isinstance(doc, dict):
        raise ValidationError(path, "expected a mapping at the top level")
    return doc


def load_schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def check_schema(doc: dict, schema_name: str, path: pathlib.Path) -> None:
    """Validate against JSON Schema when jsonschema is installed.

    Absent the library we skip rather than half-check: the structural rules in
    Course/Lesson below are the ones that cause silent breakage in production,
    and they run unconditionally. CI installs jsonschema, so the full check is
    never actually skipped where it matters.
    """
    try:
        import jsonschema
        from referencing import Registry, Resource
    except ImportError:                                        # pragma: no cover
        return

    registry = Registry()
    for f in SCHEMAS.glob("*.schema.json"):
        registry = registry.with_resource(
            f.name, Resource.from_contents(json.loads(f.read_text(encoding="utf-8")))
        )
    validator = jsonschema.Draft202012Validator(load_schema(schema_name), registry=registry)
    errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        loc = ".".join(str(p) for p in first.path) or "(root)"
        raise ValidationError(path, f"{loc}: {first.message}")


# --------------------------------------------------------------------------- #
# model
# --------------------------------------------------------------------------- #

@dataclasses.dataclass
class Deck:
    slot: str                     # "lecture" | "prestudy"
    entry: pathlib.Path           # absolute path to the deck HTML
    root: pathlib.Path            # the deck directory

    @property
    def exists(self) -> bool:
        return self.entry.is_file()


@dataclasses.dataclass
class Lesson:
    slug: str
    root: pathlib.Path
    spec: dict
    decks: dict[str, Deck]

    @property
    def week(self) -> int:
        return self.spec["week"]

    @property
    def incomplete(self) -> list[str]:
        """Slots whose HTML is not on disk. A lesson with any is not deployable."""
        return [slot for slot, deck in self.decks.items() if not deck.exists]


@dataclasses.dataclass
class Course:
    lang: str                     # directory name == GT_CLASS_COURSE.LANG_TYPE, lowercased
    slug: str
    root: pathlib.Path
    spec: dict
    lessons: list[Lesson]

    @property
    def key(self) -> str:
        """Identity in the state lock. Stable for the life of the course."""
        return f"{self.lang}/{self.slug}"

    @property
    def lang_type(self) -> str:
        return self.lang.upper()

    @property
    def curriculum_type_key(self) -> str:
        """le_tutor_curriculum.curriculum_type, as class_course_ps.php composes it."""
        return f"PODO_{self.lang_type}_{self.spec['curriculumType']}"

    @property
    def thumbnail(self) -> pathlib.Path | None:
        """The cover image on disk, or None when the course does not name one.

        None means "leave BOOK_THUMBNAIL alone", not "clear it". apply attaches no
        cover part, and grape only writes the column when one arrives — so a cover
        uploaded by hand in grape admin survives a course that says nothing about it.
        """
        rel = self.spec.get("thumbnail")
        return self.root / rel if rel else None

    @property
    def incomplete(self) -> list[Lesson]:
        return [l for l in self.lessons if l.incomplete]


def load_curriculum() -> dict:
    doc = load_yaml(REPO / "curriculum.yaml")
    check_schema(doc, "curriculum.schema.json", REPO / "curriculum.yaml")
    return doc


def load_lesson(root: pathlib.Path) -> Lesson:
    path = root / "lesson.yaml"
    doc = load_yaml(path)
    check_schema(doc, "lesson.schema.json", path)
    spec = doc["spec"]

    if doc["metadata"]["slug"] != root.name:
        raise ValidationError(
            path,
            f"slug '{doc['metadata']['slug']}' does not match directory '{root.name}' — "
            "the slug is the identity the state lock binds to, so the two must agree",
        )

    decks = {
        slot: Deck(slot=slot, entry=root / cfg["entry"], root=root / slot)
        for slot, cfg in spec["decks"].items()
    }
    return Lesson(slug=root.name, root=root, spec=spec, decks=decks)


def load_course(root: pathlib.Path, lang: str) -> Course:
    path = root / "course.yaml"
    doc = load_yaml(path)
    check_schema(doc, "course.schema.json", path)

    if doc["metadata"]["slug"] != root.name:
        raise ValidationError(
            path,
            f"slug '{doc['metadata']['slug']}' does not match directory '{root.name}'",
        )

    lesson_dir = root / "lessons"
    lessons = [
        load_lesson(d) for d in sorted(lesson_dir.iterdir())
        if d.is_dir() and (d / "lesson.yaml").is_file()
    ] if lesson_dir.is_dir() else []

    course = Course(lang=lang, slug=root.name, root=root, spec=doc["spec"], lessons=lessons)
    _check_weeks(course, path)
    _check_thumbnail(course, path)
    return course


def _check_weeks(course: Course, path: pathlib.Path) -> None:
    """CLASS_WEEK must run 1..N with no gaps and no repeats.

    The app pages a learner through a course by week number, so a gap strands
    everyone at the hole and a duplicate makes which lesson they get arbitrary.
    """
    weeks = [l.week for l in course.lessons]
    if not weeks:
        return
    dupes = sorted({w for w in weeks if weeks.count(w) > 1})
    if dupes:
        raise ValidationError(path, f"CLASS_WEEK reused by more than one lesson: {dupes}")
    expected = list(range(1, len(weeks) + 1))
    if sorted(weeks) != expected:
        missing = sorted(set(expected) - set(weeks))
        raise ValidationError(
            path, f"weeks must run 1..{len(weeks)} with no gaps; missing {missing}"
        )


def _check_thumbnail(course: Course, path: pathlib.Path) -> None:
    """The cover must be an image that exists, inside the course directory.

    Every failure here is silent downstream. A path with a typo makes apply send no
    cover at all, grape leaves BOOK_THUMBNAIL alone by design, and the course keeps
    the old picture while the YAML says it has a new one — the deploy is green and
    nothing anywhere reports a miss.
    """
    thumb = course.thumbnail
    if thumb is None:
        return

    rel = course.spec["thumbnail"]
    try:
        thumb.resolve().relative_to(course.root.resolve())
    except (ValueError, OSError):
        raise ValidationError(
            path, f"thumbnail '{rel}' points outside the course directory — "
                  "the cover has to live with the course that ships it")

    if not thumb.is_file():
        raise ValidationError(path, f"thumbnail '{rel}' is not on disk")

    if thumb.suffix.lower() not in THUMBNAIL_SUFFIXES:
        kinds = ", ".join(sorted(THUMBNAIL_SUFFIXES))
        raise ValidationError(
            path, f"thumbnail '{rel}' is not one of {kinds} — grape decides the "
                  "format from the bytes and rejects anything else")

    size = thumb.stat().st_size
    if size > THUMBNAIL_MAX_BYTES:
        raise ValidationError(
            path, f"thumbnail '{rel}' is {size // 1024} KB; the cap is "
                  f"{THUMBNAIL_MAX_BYTES // 1024} KB — it is a list thumbnail, not a page image")


def discover() -> list[Course]:
    """Every deployable course in the repo.

    Only courses/ is ever walked. sandbox/ and references/ are not excluded by a
    list that could drift — they are simply never reached.
    """
    if not COURSES.is_dir():
        return []
    found = []
    for lang_dir in sorted(COURSES.iterdir()):
        if not lang_dir.is_dir() or lang_dir.name.startswith("."):
            continue
        for course_dir in sorted(lang_dir.iterdir()):
            if course_dir.is_dir() and (course_dir / "course.yaml").is_file():
                found.append(load_course(course_dir, lang_dir.name))
    return found


# --------------------------------------------------------------------------- #
# state lock
# --------------------------------------------------------------------------- #

