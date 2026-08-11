The 예습용 deck goes here as `index.html`, alongside its own `assets/`.

It is not optional. A lesson with only a 수업용 deck leaves
`PRESTUDY_LEMONBOARD_KEY` empty, and class creation in podo-backend then fails at
`/rooms/null/duplicate`. `tools/validate.py` blocks the merge for that reason —
this lesson is deliberately in that state until the deck is written.

Delete this file once the deck exists.
