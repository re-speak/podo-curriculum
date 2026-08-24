#!/usr/bin/env python3
"""Regression contract for shared tutor-note placement."""

from __future__ import annotations

import json
import pathlib
import subprocess
import textwrap
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "shared/js/tutor-notes.js"
TRIAL_CSS = ROOT / "shared/css/trial.css"


HARNESS = r"""
const fs = require("fs");
const vm = require("vm");

class ClassList {
  constructor(values) { this.values = new Set(values || []); }
  add(value) { this.values.add(value); }
  contains(value) { return this.values.has(value); }
}

class Element {
  constructor(tag, classes, attributes) {
    this.tagName = tag.toUpperCase();
    this.classList = new ClassList(classes);
    this.attributes = Object.assign({}, attributes);
    this.children = [];
    this.parent = null;
    this.readOnly = false;
  }
  set className(value) { this.classList = new ClassList(value.split(/\s+/).filter(Boolean)); }
  get className() { return [...this.classList.values].join(" "); }
  appendChild(child) {
    child.parent = this;
    this.children.push(child);
    return child;
  }
  setAttribute(name, value) { this.attributes[name] = value; }
  getAttribute(name) { return this.attributes[name] || null; }
  addEventListener() {}
  matches(selector) {
    return selector.split(",").some((part) => {
      const name = part.trim().replace(/^\./, "");
      return this.classList.contains(name);
    });
  }
  querySelector(selector) {
    let predicate;
    const classMatch = selector.match(/^:scope > \.([a-z0-9-]+)$/i);
    if (classMatch) {
      predicate = (child) => child.classList.contains(classMatch[1]);
    } else if (selector === ":scope > [data-note-anchor]") {
      predicate = (child) => Object.hasOwn(child.attributes, "data-note-anchor");
    } else {
      return null;
    }
    return this.children.find(predicate) || null;
  }
  querySelectorAll(selector) {
    const found = [];
    const visit = (node) => {
      node.children.forEach((child) => {
        if (selector === ".note-input" && child.classList.contains("note-input")) found.push(child);
        visit(child);
      });
    };
    visit(this);
    return found;
  }
  insertAdjacentElement(position, child) {
    if (position !== "afterend" || !this.parent) throw new Error("unsupported insertion");
    const index = this.parent.children.indexOf(this);
    child.parent = this.parent;
    this.parent.children.splice(index + 1, 0, child);
  }
}

function child(name, attributes) { return new Element("div", [name], attributes); }
function run(pageClasses, childSpecs) {
  const phone = new Element("main", ["phone"]);
  const page = new Element("section", pageClasses, {"data-page-id": "test-page"});
  childSpecs.forEach((spec) => page.appendChild(child(spec[0], spec[1])));
  phone.appendChild(page);

  const document = {
    body: {classList: new ClassList(["teaching"])},
    querySelector(selector) {
      if (selector === ".phone") return phone;
      return null;
    },
    createElement(tag) { return new Element(tag); }
  };
  class MutationObserver { observe() {} }
  vm.runInNewContext(fs.readFileSync(process.argv[1], "utf8"), {document, MutationObserver});

  const box = phone.querySelectorAll(".note-input")[0];
  return {
    order: page.children.map((item) => item.classList.values.has("note-input") ? "memo" : [...item.classList.values][0]),
    docked: box.classList.contains("note-input--dock")
  };
}

const cases = {
  transition: run(["transition-page"], [["transition-title"], ["transition-copy"]]),
  transitionScript: run(["transition-page"], [["section-subtitle"], ["tutor-note"], ["known"]]),
  brand: run(["brand-page", "bleed"], [["brand-title"], ["end-card"]]),
  explicit: run(["section"], [["section-title"], ["custom", {"data-note-anchor": ""}], ["activity"]]),
  script: run(["section"], [["section-subtitle"], ["tutor-note"], ["activity"]]),
  report: run(["section", "report"], [["rhead"], ["report-body"], ["tutor-note"]]),
  info: run(["section", "info-page"], [["section-title"], ["info-body"], ["tutor-note"]])
};
process.stdout.write(JSON.stringify(cases));
"""


class TutorNotesRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        result = subprocess.run(
            ["node", "-e", textwrap.dedent(HARNESS), str(RUNTIME)],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.cases = json.loads(result.stdout)

    def test_full_screen_pages_are_docked_outside_the_centered_flow(self) -> None:
        self.assertEqual(
            self.cases["transition"],
            {"order": ["transition-title", "transition-copy", "memo"], "docked": True},
        )
        self.assertEqual(
            self.cases["brand"],
            {"order": ["brand-title", "end-card", "memo"], "docked": True},
        )

    def test_content_heavy_transition_keeps_the_memo_with_its_script(self) -> None:
        self.assertEqual(
            self.cases["transitionScript"],
            {
                "order": ["section-subtitle", "tutor-note", "memo", "known"],
                "docked": False,
            },
        )

    def test_explicit_anchor_wins_on_an_ordinary_page(self) -> None:
        self.assertEqual(
            self.cases["explicit"]["order"],
            ["section-title", "custom", "memo", "activity"],
        )

    def test_ordinary_script_keeps_the_memo_after_the_tutor_note(self) -> None:
        self.assertEqual(
            self.cases["script"]["order"],
            ["section-subtitle", "tutor-note", "memo", "activity"],
        )
        self.assertFalse(self.cases["script"]["docked"])

    def test_long_pages_put_the_memo_near_the_heading(self) -> None:
        self.assertEqual(
            self.cases["report"]["order"],
            ["rhead", "memo", "report-body", "tutor-note"],
        )
        self.assertEqual(
            self.cases["info"]["order"],
            ["section-title", "memo", "info-body", "tutor-note"],
        )

    def test_dock_css_has_safe_insets_and_a_growth_limit(self) -> None:
        css = TRIAL_CSS.read_text(encoding="utf-8")
        self.assertIn(".brand-page > .note-input--dock", css)
        self.assertIn(".transition-page > .note-input--dock", css)
        self.assertIn("max-height: min(132px, 24vh)", css)
        self.assertIn("bottom: var(--pager-clearance)", css)


if __name__ == "__main__":
    unittest.main()
