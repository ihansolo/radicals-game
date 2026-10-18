#!/usr/bin/env python3
"""
Step 1 of the puzzle pipeline: build a curated character database.

Input:  data/dictionary.txt  (the Make Me a Hanzi dataset)
Output: data/hanzi_db.json   (curated characters + their teachable radicals)

What it does:
- Reads the open Make Me a Hanzi decomposition dataset.
- Maps transformed radical forms back to their parent radical
  (氵->水, 灬->火, 亻->人, 忄->心, 扌->手, etc.).
- Keeps only a hand-curated list of common, kid-friendly TRADITIONAL
  characters (see COMMON below), each tagged with the teachable radicals
  genuinely inside it.

The curation is deliberate: the raw dataset has ~6000 characters with a
teachable radical, but many are obscure. For a learning game we want a
controlled, age-appropriate set. Grow COMMON (and TEACHABLE / RAD_MEAN /
RAD_PIN) as the game expands toward a larger character pool.
"""
import json, os

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "data")

# Transformed radical form -> parent radical it teaches.
RADICAL_PARENT = {
    '氵':'水','灬':'火','亻':'人','忄':'心','扌':'手','艹':'艸',
    '辶':'辵','犭':'犬','纟':'糸','糹':'糸','讠':'言','訁':'言',
    '飠':'食','刂':'刀','冫':'冰','礻':'示','衤':'衣',
}

# Parent radicals we allow as puzzle hints (common, kid-friendly), with
# English meaning and standalone Mandarin reading (pinyin).
RAD_INFO = {
    '日':('sun','rì'),   '月':('moon','yuè'),  '木':('tree','mù'),
    '水':('water','shuǐ'),'火':('fire','huǒ'), '人':('person','rén'),
    '口':('mouth','kǒu'),'心':('heart','xīn'), '手':('hand','shǒu'),
    '言':('speech','yán'),'女':('woman','nǚ'), '山':('mountain','shān'),
    '田':('field','tián'),'目':('eye','mù'),   '力':('strength','lì'),
    '土':('earth','tǔ'), '金':('metal','jīn'),
}
TEACHABLE = set(RAD_INFO.keys())

# Curated common traditional characters the game may use. Each will be kept
# only if the dataset confirms it contains at least one teachable radical.
COMMON = [
 '明','朋','林','森','晶','男','加','叫','吃','時','晚','春','是','星',
 '休','你','他','住','信','個','們','作','做','體','像',
 '河','海','江','湖','洗','流','清','深','滿','油','活',
 '熱','照','烈','然','點','煮',
 '想','思','怕','快','慢','忙','情','愛','感','息',
 '打','找','拿','推','拉','提','接','把','抱','拍',
 '說','話','語','請','謝','讀','課','記','認','識',
 '好','媽','姐','妹','她','婚','始','姓','安','字',
 '山','岩','島','峰',
 '界','留','畫','當',
 '看','眼','睛','睡','着',
 '助','動','努','勞',
 '地','場','坐','城','在','坡','塊',
 '錢','銀','鐵','鏡','針',
]

def parent_of(rad):
    return RADICAL_PARENT.get(rad, rad)

def top_components(decomp):
    """Return leaf components of an IDS decomposition string, ignoring the
    structure operators (⿰⿱ etc.) and unknown-component markers."""
    ops = set('⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻')
    return [c for c in decomp if c not in ops and c != '？']

def teachable_radicals_in(entry):
    """Teachable parent radicals genuinely present in a character entry."""
    found = set()
    p = parent_of(entry.get('radical', ''))
    if p in TEACHABLE:
        found.add(p)
    for comp in top_components(entry.get('decomposition', '')):
        p2 = parent_of(comp)
        if p2 in TEACHABLE:
            found.add(p2)
    return found

def main():
    chars = {}
    with open(os.path.join(DATA, "dictionary.txt"), encoding="utf-8") as f:
        for line in f:
            o = json.loads(line)
            chars[o['character']] = o

    db = {}
    for c in dict.fromkeys(COMMON):  # dedup, preserve order
        o = chars.get(c)
        if not o:
            continue
        rads = teachable_radicals_in(o)
        if not rads:
            continue
        db[c] = {
            'rads': sorted(rads),
            'def': (o.get('definition') or '')[:40],
            'pinyin': (o.get('pinyin') or [''])[0],
            'radical': o.get('radical', ''),      # transformed form, for reveal text
            'decomp': o.get('decomposition', ''),
        }

    out = os.path.join(DATA, "hanzi_db.json")
    json.dump(db, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    multi = sum(1 for v in db.values() if len(v['rads']) >= 2)
    print(f"Wrote {out}: {len(db)} characters, {multi} multi-radical (puzzle anchors).")

if __name__ == "__main__":
    main()
