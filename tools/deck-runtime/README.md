# deck-runtime

The one runtime file this repo owns rather than mirrors.

Everything else under `shared/js` comes from `beginner-curriculum/korean/runtime`
untouched. `activities.js` cannot: upstream's version **creates** the input
controls at load, promoting `<span class="slot">` and `<span class="answer-space">`
shells into `<input>` / `<textarea>` and carrying `data-sync-id` across.

lemonboard's validator parses the HTML statically (`parseHTML` via linkedom, no
scripts run), so those shells resolve to no `data-sync-kind` and are dropped from
the sync set — while the binder, which re-scans the live DOM, picks them up fine.
The deck then works in class and fails the merge gate, which is indistinguishable
from a deck that is genuinely broken.

So `import-trial-decks.py` writes the real controls into the markup and bundles
this version, which **binds** them instead of creating them. Grading, answer-width
sizing, chip reordering and the `order` kind registration are unchanged from
upstream.

If upstream changes how an activity behaves, port the change here by hand — there
is no automatic path, because the two files differ by design.
