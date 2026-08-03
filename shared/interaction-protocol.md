# Interactive lessons — the `data-sync` contract

How a lesson page shares state between the tutor and the learner on
[lemonboard](https://github.com/re-speak/lemonboard).

> **Read this before adding any interaction to a lesson.** Getting the contract wrong
> fails silently: the activity looks fine on your screen and simply never reaches the
> other person.

**Reference implementation:** [`sample-lesson-interactive.html`](./sample-lesson-interactive.html).
Copy from it rather than inventing markup.

---

## The one idea

**Lemonboard owns the transport. The lesson owns the meaning.**

The board carries an opaque blob of JSON per shared element. It has no idea what a
"tile" or a "syllable" is, and it must never learn — that is what keeps you from
needing a board change every time you invent an activity.

So the board handles all of this, and you never write it again:

- delivering state to the other participant
- catching up someone who joins late or reloads mid-lesson
- suppressing echoes so an applied change isn't sent back
- converging when both people touch the same thing at once

And the lesson decides only two things: **what is shared**, and **what that state means**.

### State, not events

You share the *result*, never the click.

This matters more than it sounds. If you broadcast "the next button was clicked",
a learner who reloads has nothing to replay, and a single dropped message desyncs the
two of you permanently. If you share "we are on page 5", a reload catches up from one
snapshot and any drift self-corrects on the next update.

Write `read`/`apply` to answer *"what is true now?"* — never *"what just happened?"*

### Grading is not shared

Send the choice, not the verdict. Both sides run the same page code, so both derive
`correct`/`wrong` themselves from `data-ok` (or whatever your answer key is).

Two reasons. Derived state that travels goes stale and contradicts what the receiving
page would compute; and a tutor-only reveal has to stay tutor-only, which it can't if
the verdict is broadcast the moment the tutor sees it.

> **This does not hide the answer key.** Both participants load the same document, so
> `data-ok`, `data-correct`, `data-answers` and the initial text of a `.slot` are all in
> the learner's DOM already. What the contract guarantees is that the *reveal toggle* and
> the *verdict* aren't pushed across. If an answer must genuinely be unavailable to the
> learner, it cannot live in the lesson HTML at all.

---

## Marking something as shared

Put `data-sync-id` on the element. That is the whole opt-in.

```html
<div class="tap-grid" data-sync-id="tiles-find-the-vowel" ...>
```

- The id is the sync key, so it must be **unique in the page** and **stable across
  edits** — it is what a reconnecting peer matches on. Use kebab-case that describes
  the activity (`tiles-find-the-vowel`), never a position (`grid-3`), so inserting a
  page above it doesn't silently repoint the state.
- **No `data-sync-id` means private.** That is how you keep something local: a
  self-assessment checklist, a tutor's answer reveal, a personal view preference.
  There is no "local" marker to add — just don't give it an id.

If a placeholder is replaced by a real control at runtime, hand the id over so exactly
one live element carries it (see `transferSyncMetadata` in the sample).

---

## Built-in kinds — no JavaScript at all

`data-sync-kind` names how to read and apply the element. Three kinds ship with the
board and cover most activities.

### `value` — text entry

Any `<input>`, `<textarea>` or `<select>`. **Inferred**, so you can omit the attribute.

```html
<input data-sync-id="answer-copula" />
```

The board watches typing, holds back mid-IME composition (so Korean/Japanese doesn't
arrive half-composed), and clamps at 2000 characters.

### `selection` — one *or* many choices

The set of `[data-sync-option]` descendants currently carrying an active class.

```html
<div class="tap-grid"
     data-sync-id="tiles-find-the-vowel"
     data-sync-kind="selection"
     data-sync-state="right wrong">
  <button class="tap-tile" data-sync-option="na" data-ok>나</button>
  <button class="tap-tile" data-sync-option="meo">머</button>
</div>
```

- `data-sync-state` lists the classes that mean "active" — any one of them counts.
  Two are listed here because a tapped tile becomes either `right` or `wrong`.
- Only the chosen ids travel. `right`/`wrong` is re-derived on each side from `data-ok`.

**Single-choice uses this same kind.** A radio group is just a set with room for one,
and that rule belongs in your click handler, not in the board:

```js
opts.forEach(o => o.classList.remove('chosen'));   // ← this is what makes it single-choice
opt.classList.add('chosen');
```

Remote state is applied by **clicking** the options that differ, so your own handler
runs and derives everything downstream. Two consequences worth knowing: side effects
in that handler (audio, animation) will fire on the receiving side too, and the active
class must be **persistent** — a class you strip after 700ms is invisible to `read`.

### `toggle` — on/off

Whether the element itself carries an active class. Applied by clicking it.

```html
<li data-sync-id="mission-ask-likes" data-sync-kind="toggle" data-sync-state="checked">
```

---

## Registered kinds — when the DOM isn't the state

If the state lives in a closure — a keypad mid-composition, the current page index, a
chip pool — no generic reader can see it. Bring your own:

```js
sync.register('page', {
  read: () => ({ pageId: pages[at].dataset.pageId }),
  apply: (element, state) => { goTo(pages.findIndex(p => p.dataset.pageId === state.pageId)); },
});
```

```html
<nav class="pager" data-sync-id="deck-page" data-sync-kind="page">
```

**This needs no lemonboard change and no deploy.** It is the extension point — reach
for it whenever a built-in doesn't fit, rather than bending markup to match one.

Rules for `read`/`apply`:

- `read` returns JSON-serialisable state, and **stable output for the same state** —
  sort your arrays, or you'll republish on every interaction.
- `apply` must be **idempotent**: applying the same state twice equals applying it once.
- `apply` must tolerate junk (a page id this deck doesn't have, a wrong shape) and
  do nothing rather than throw.
- Name state by **meaning, not position** — `{ pageId: 'find-the-vowel' }`, not
  `{ index: 7 }`, so adding a page doesn't move everyone.

### The runtime, and working offline

Lemonboard injects `window.lessonSync` into `<head>` before your scripts run. Opening
the file straight from disk there is no board, so guard it — the lesson then still
works standalone, it just doesn't sync:

```js
const sync = window.lessonSync || {
  kinds: {},
  register: function (name, handlers) { this.kinds[name] = handlers; return this; },
  push: function () {}
};
```

### `sync.push(element)`

Click and input are watched for you, so **most activities call nothing**. Call `push`
only when state changes without one of those events — arrow-key navigation, a scroll
that changes the current page, a drag that ends, a timer:

```js
document.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight') { goTo(at + 1); sync.push(pager); }
});
```

Calling it when you didn't need to is harmless — nothing is published if nothing changed.

---

## Choosing a kind

| The state is… | Use |
|---|---|
| text someone typed | `value` (inferred — omit the attribute) |
| which options are picked, one or many | `selection` |
| one thing on or off | `toggle` |
| in a JS variable, not the DOM | `register()` your own |
| nobody else's business | no `data-sync-id` |

---

## Checklist before shipping an activity

- [ ] Every shared element has a unique, meaning-based `data-sync-id`.
- [ ] Anything private has **no** `data-sync-id`.
- [ ] Active classes used by `selection`/`toggle` are persistent, not 700ms flashes.
- [ ] The answer key is derived locally — verdicts never appear in shared state.
- [ ] `read` output is stable; `apply` is idempotent and survives junk.
- [ ] `window.lessonSync` is guarded so the file still opens standalone.
- [ ] Opened in two browser windows: interactions land on both, and a **late-joining
      third window catches up** to the current state.

Then package it — see [`packaging.md`](./packaging.md).
