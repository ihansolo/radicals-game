# 部首 Radicals — a Chinese radical-matching game

A small mobile web game for learning the radicals (部首) inside **traditional**
Chinese characters. The player sees a set of radical hints and a set of
character tiles, and places each character under the radical hidden inside it.
Some characters contain more than one radical, so the player has to reason out
which placement is forced — the same "one move unlocks the rest" feel as a
logic puzzle.

Built as a learning tool for a child. Touch-first, works on phone and iPad.

## How to play
- Tap a character to hear it pronounced (Taiwan Mandarin), then tap a radical
  slot to place it there.
- Tap a placed character to send it back down and try a different slot.
- Tap the circle under a character to "peek" — it reveals the radical inside
  (showing transformed forms like 氵→水, 灬→火, 亻→人).
- Solve the daily puzzle, or hit **New puzzle** for unlimited play.

## Play it / host it
`index.html` is one self-contained file (font and puzzles baked in, no
dependencies, works offline). To use it:
- **On a device:** open `index.html` in a browser, then (iOS) Share →
  "Add to Home Screen" for an app-like icon.
- **Online:** drag `index.html` onto https://app.netlify.com/drop for an
  instant link, or use GitHub Pages (Settings → Pages → source = main branch).

## Repo layout
```
index.html                 the finished, self-contained game (the deliverable)
scripts/
  1_build_char_db.py       curate characters + their radicals from the dataset
  2_generate_puzzles.py    generate puzzles, verified unique & solvable by logic
  3_build_app.py           subset the font + inline everything into index.html
  app_template.html        the game shell, with __FONT_BASE64__ / __BANK__ slots
data/
  dictionary.txt           Make Me a Hanzi dataset (source character data)
  hanzi_db.json            curated characters (output of step 1)
  puzzle_bank.json         the 40 puzzles the game loads (output of step 2)
fonts/
  GenJyuuGothic-Regular.woff2   full rounded CJK font (source)
  subset.woff2                  93-glyph subset actually embedded (output of step 3)
```

## Rebuilding (when you change characters or puzzles)
```
pip install fonttools brotli
python3 scripts/1_build_char_db.py
python3 scripts/2_generate_puzzles.py
python3 scripts/3_build_app.py
```
Step 1's `COMMON` list is the set of characters the game may use — edit it to
grow or change the pool. Step 2's `N_TILES` and `WANT_OVERLAP` control puzzle
size and difficulty. Every generated puzzle is checked to have exactly one
solution reachable without guessing.

## Known limits / next steps
- The character pool is ~100 hand-curated characters, not the full common set.
  Expanding toward 2500–3500 characters means growing `COMMON` and adding a
  review pass over the dataset's decompositions (some are historically accurate
  but confusing for a learner).
- Radical pinyin is a small hand-made map in the scripts (16 radicals); extend
  `RAD_INFO` as you add radicals.

## Credits & licenses
- Character data: **Make Me a Hanzi** (github.com/skishore/makemeahanzi) —
  code under LGPL; character data derived from Unicode CJK sources and CC-CEDICT.
- Font: **GenJyuuGothic / 源柔黑體** (rounded, derived from Source Han Sans),
  distributed under the SIL Open Font License 1.1.
- Game code: yours to do with as you like.
