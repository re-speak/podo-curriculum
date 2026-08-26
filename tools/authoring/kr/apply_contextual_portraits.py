#!/usr/bin/env python3
"""Apply the reviewed contextual-course cast map to canonical draft decks.

Portrait identity lives in ``portrait-cast.json``. This small source transform
keeps hand-authored courses aligned with the generated six without treating
rendered HTML as the place where casting decisions are made.
"""

from __future__ import annotations

import json
import pathlib
import re


REPO = pathlib.Path(__file__).resolve().parents[3]
TRACK = REPO / 'sandbox/drafts/kr/tracks/3-contextual-korean'
COURSES = TRACK / 'courses'
CAST_PATH = TRACK / 'portrait-cast.json'
PORTRAIT_DIR = REPO / 'shared/assets'
PORTRAIT_PREFIX = '../../../../../../../../../shared/assets/'

ICON = ('<span class="avatar icon"><svg aria-hidden="true" viewBox="0 0 24 24">'
        '<path d="M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10Zm0 2.5c-4.7 0-8.5 '
        '2.6-8.5 5.8V22h17v-1.7c0-3.2-3.8-5.8-8.5-5.8Z" fill="currentColor"/>'
        '</svg></span>')

WHO = re.compile(
    r'(?P<avatar><img\b[^>]*class="avatar"[^>]*>|<span class="avatar icon">.*?</span>)'
    r'(?P<label><span class="who-name">(?P<role>[^<]+)</span>)'
)
CAST = re.compile(
    r'(?P<avatar><img\b[^>]*class="avatar"[^>]*>|<span class="avatar icon">.*?</span>)'
    r'(?P<label><span class="cast-who">(?P<role>[^<]+)<small>)'
)


def avatar(role: str, cast: dict[str, str]) -> str:
    if role == '선생님' or role.startswith('나'):
        return ICON
    filename = cast.get(role)
    if not filename:
        raise ValueError(f'no portrait assignment for role {role!r}')
    if not (PORTRAIT_DIR / filename).is_file():
        raise ValueError(f'portrait asset does not exist: {filename}')
    return f'<img alt="" class="avatar" src="{PORTRAIT_PREFIX}{filename}"/>'


def apply(path: pathlib.Path, cast: dict[str, str]) -> bool:
    source = path.read_text()

    def replace(match: re.Match[str]) -> str:
        role = match.group('role')
        current = match.group('avatar')
        if (role == '선생님' or role.startswith('나')) and current.startswith('<span'):
            return current + match.group('label')
        return avatar(role, cast) + match.group('label')

    rendered = WHO.sub(replace, source)
    rendered = CAST.sub(replace, rendered)
    if rendered == source:
        return False
    path.write_text(rendered)
    return True


def main() -> int:
    assignments = json.loads(CAST_PATH.read_text())
    changed = 0
    for course, cast in assignments.items():
        for path in sorted((COURSES / course / 'lessons').glob('*/lesson.html')):
            changed += apply(path, cast)
    print(f'updated {changed} contextual lesson deck(s)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
