#!/usr/bin/env python3
"""
Step 3 of the pipeline: build the final, self-contained index.html.

Inputs:
  app_template.html                     (the game, with two placeholders)
  data/puzzle_bank.json                 (from step 2)
  fonts/GenJyuuGothic-Regular.woff2     (full rounded font, from googlefonts/chinese)

Output:
  ../index.html                         (one self-contained file, ready to host)

What it does:
- Figures out exactly which characters the puzzles use (~90 glyphs).
- Subsets the big rounded CJK font down to just those glyphs (tens of KB,
  instead of ~3.4 MB) so the page loads instantly and works offline.
- Inlines the subset font as base64 and the puzzle bank as JSON into the
  template, replacing the __FONT_BASE64__ and __BANK__ placeholders.

Requires: pip install fonttools brotli
"""
import json, os, base64
from fontTools import subset
from fontTools.ttLib import TTFont

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")
DATA = os.path.join(ROOT, "data")
FONTS = os.path.join(ROOT, "fonts")

def charset_from_bank(bank):
    chars = set("部首")  # brand title in the header
    for p in bank:
        for t in p['tiles']:
            chars.add(t['char'])
            for part in t['reveal'].replace('→', ''):
                chars.add(part)
        for h in p['hints']:
            chars.add(h['r'])
    return "".join(sorted(chars))

def subset_font(text):
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = "*"
    opts.notdef_outline = True
    font = TTFont(os.path.join(FONTS, "GenJyuuGothic-Regular.woff2"))
    ss = subset.Subsetter(options=opts)
    ss.populate(text=text)
    ss.subset(font)
    out = os.path.join(FONTS, "subset.woff2")
    font.save(out)
    return out

def main():
    bank = json.load(open(os.path.join(DATA, "puzzle_bank.json"), encoding="utf-8"))
    text = charset_from_bank(bank)

    sub_path = subset_font(text)
    b64 = base64.b64encode(open(sub_path, "rb").read()).decode()
    print(f"Font subset: {len(text)} glyphs, {os.path.getsize(sub_path)//1024} KB.")

    template = open(os.path.join(HERE, "app_template.html"), encoding="utf-8").read()
    html = template.replace("__FONT_BASE64__", b64)
    html = html.replace("__BANK__", json.dumps(bank, ensure_ascii=False))

    out = os.path.join(ROOT, "index.html")
    open(out, "w", encoding="utf-8").write(html)
    print(f"Wrote {out}: {len(html)//1024} KB, self-contained.")

if __name__ == "__main__":
    main()
