#!/usr/bin/env python3
"""
Step 2 of the puzzle pipeline: generate solver-verified puzzles.

Input:  data/hanzi_db.json   (from step 1)
Output: data/puzzle_bank.json (the puzzles the game loads)

The mechanic: each puzzle shows N radical "hints" and N character "tiles".
Every character genuinely contains more than one teachable radical, which
creates ambiguity; the player must deduce which character goes under which
radical. A puzzle is only kept if it has EXACTLY ONE solution AND that
solution is reachable by pure constraint propagation (no guessing).

Two checks enforce quality:
- solve():    brute-force all assignments, keep only puzzles with 1 solution.
- deducible(): simulate forced-move propagation; the puzzle must fully resolve
               with no arbitrary choice.

Tune N (tiles per puzzle) and WANT_OVERLAP (minimum multi-radical tiles) to
change difficulty. Current game uses 5 tiles, >=2 overlap (mixed difficulty).
"""
import json, os, random
from itertools import permutations

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "data")

# Radical -> (english meaning, pinyin). Kept in sync with step 1's RAD_INFO.
RAD_INFO = {
    '日':('sun','rì'),   '月':('moon','yuè'),  '木':('tree','mù'),
    '水':('water','shuǐ'),'火':('fire','huǒ'), '人':('person','rén'),
    '口':('mouth','kǒu'),'心':('heart','xīn'), '手':('hand','shǒu'),
    '言':('speech','yán'),'女':('woman','nǚ'), '山':('mountain','shān'),
    '田':('field','tián'),'目':('eye','mù'),   '力':('strength','lì'),
    '土':('earth','tǔ'), '金':('metal','jīn'),
}

# Transformed form shown when the player peeks (e.g. "氵→水"); plain parent otherwise.
INV_TRANSFORM = {'氵':'水','灬':'火','亻':'人','忄':'心','扌':'手'}

N_TILES = 5          # characters (and hints) per puzzle
WANT_OVERLAP = 2     # minimum number of multi-radical tiles, for deduction tension
TARGET_COUNT = 40    # how many puzzles to generate
SEED = 11            # fixed seed -> reproducible bank

def load_db():
    return json.load(open(os.path.join(DATA, "hanzi_db.json"), encoding="utf-8"))

def shown_form(db, c, parent):
    rf = db[c]['radical']
    if INV_TRANSFORM.get(rf) == parent and rf != parent:
        return f"{rf}→{parent}"
    return parent

def solve(db, tiles, hints):
    """All valid complete assignments (stop at 2 — we only care if unique)."""
    sols = []
    for perm in permutations(hints, len(tiles)):
        if all(perm[i] in db[tiles[i]]['rads'] for i in range(len(tiles))):
            sols.append(dict(zip(tiles, perm)))
            if len(sols) > 1:
                return sols
    return sols

def deducible(db, tiles, hints):
    """True if the single solution is reachable by forced moves only."""
    used, rem, progress = set(), set(tiles), True
    while progress and rem:
        progress = False
        for t in list(rem):                                   # a tile with one option left
            opts = [h for h in hints if h in db[t]['rads'] and h not in used]
            if len(opts) == 1:
                used.add(opts[0]); rem.discard(t); progress = True
        for h in hints:                                       # a hint only one tile can fill
            if h in used:
                continue
            cand = [t for t in rem if h in db[t]['rads']]
            if len(cand) == 1:
                used.add(h); rem.discard(cand[0]); progress = True
    return not rem

def gen_one(db, chars, tries=12000):
    for _ in range(tries):
        pick = random.sample(chars, N_TILES)
        if sum(len(db[c]['rads']) >= 2 for c in pick) < WANT_OVERLAP:
            continue
        # choose a candidate solution (most-constrained tiles first), distinct radicals
        sol, used, ok = {}, set(), True
        for c in sorted(pick, key=lambda c: len(db[c]['rads'])):
            opts = [r for r in db[c]['rads'] if r not in used]
            if not opts:
                ok = False; break
            r = random.choice(opts); sol[c] = r; used.add(r)
        if not ok or len(used) != N_TILES:
            continue
        hints = list(used)
        if len(solve(db, pick, hints)) != 1 or not deducible(db, pick, hints):
            continue
        return {'tiles': pick, 'hints': hints, 'solution': sol}
    return None

def main():
    random.seed(SEED)
    db = load_db()
    chars = list(db.keys())
    bank, seen, guard = [], set(), 0
    while len(bank) < TARGET_COUNT and guard < 8000:
        guard += 1
        p = gen_one(db, chars)
        if not p:
            continue
        key = tuple(sorted(p['tiles']))
        if key in seen:
            continue
        seen.add(key)
        tiles = [{
            'char': c,
            'pinyin': db[c]['pinyin'],
            'reveal': shown_form(db, c, p['solution'][c]),
            'def': db[c]['def'],
        } for c in p['tiles']]
        hints = [{'r': r, 'm': RAD_INFO.get(r, ('',''))[0], 'p': RAD_INFO.get(r, ('',''))[1]}
                 for r in p['hints']]
        bank.append({'tiles': tiles, 'hints': hints, 'solution': p['solution']})

    out = os.path.join(DATA, "puzzle_bank.json")
    json.dump(bank, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f"Wrote {out}: {len(bank)} puzzles ({N_TILES} tiles each, verified unique + deducible).")

if __name__ == "__main__":
    main()
