#!/usr/bin/env python3
"""Decide which slot the correct option takes on each row of a choice page.

Generators used to write ``if index % 2: options.reverse()``, which produces
left, right, left, right down every page. That reads as variety and is not:
the learner picks the alternation up on row three and stops reading the
sentence, because following the pattern pays out faster than decoding. A fixed
slot is the same defect one step earlier, and both are what
``check_deck.choice_position_issues`` refuses.

What replaces it has to be *deterministic* — a generator that emits different
bytes on every run turns "did this change?" into an unanswerable question, and
the English batch tests compare generated output to the committed file byte for
byte. So the sequence is chosen by hashing a key the page already owns rather
than by a random draw, and the same key always yields the same page.

Rows are not shuffled and options are not reordered relative to each other in
meaning: only which of the two slots holds the correct one moves.
"""

from __future__ import annotations

import hashlib
from itertools import product


def _learnable(slots: tuple[int, ...]) -> bool:
    """Is this sequence one a learner can follow instead of reading?"""
    if len(set(slots)) == 1:
        return True                                   # always the same slot
    return all(a != b for a, b in zip(slots, slots[1:]))   # strict alternation


def _candidates(count: int) -> list[tuple[int, ...]]:
    return [s for s in product((0, 1), repeat=count) if not _learnable(s)]


def correct_slots(key: str, count: int) -> list[int]:
    """Return the slot (0 = first, 1 = second) of the correct option per row.

    ``key`` is any stable string the page owns — a sync id prefix or page id is
    ideal, because it differs between pages of one deck and does not change when
    the deck is regenerated.

    Fewer than three rows cannot establish a pattern, so they are left in the
    plain alternating order the old code produced; ``choice_position_issues``
    does not judge them either. From three rows up, the sequence is drawn from
    the set that is neither constant nor strictly alternating.
    """
    if count < 3:
        return [index % 2 for index in range(count)]
    options = _candidates(count)
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return list(options[int.from_bytes(digest, "big") % len(options)])
