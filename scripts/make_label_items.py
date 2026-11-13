"""Draw the blind human-labelling sample: 100 replies, stratified so every model,
mode and label appears; seed fixed. The first 40 are also labelled by a second person.

Usage: python scripts/make_label_items.py results/main.jsonl [more results...]
Writes label/items.json (shown to labellers: no model or system prompt) and
label/key.json (maps item id to the full record, for analysis).
"""
import json
import random
import sys

prompts = {}
for line in open("data/prompts/main.jsonl"):
    r = json.loads(line)
    prompts[r["id"]] = r

recs = []
for path in sys.argv[1:]:
    for line in open(path):
        r = json.loads(line)
        p = prompts.get(r["prompt_id"])
        if p and r.get("response"):
            recs.append((p, r))

rnd = random.Random(2026)
rnd.shuffle(recs)
# Stratify: round-robin over (model, label, mode) cells.
cells = {}
for p, r in recs:
    cells.setdefault((r["model"], p["label"], p["mode"]), []).append((p, r))
order = sorted(cells)
rnd.shuffle(order)
picked = []
while len(picked) < 100 and any(cells.values()):
    for c in order:
        if cells[c] and len(picked) < 100:
            picked.append(cells[c].pop())

items, key = [], {}
for n, (p, r) in enumerate(picked):
    iid = f"i{n:03d}"
    user = [m["content"] for m in p["messages"] if m["role"] == "user"][-1]
    items.append({"id": iid, "user": user, "reply": r["response"], "writes_message": p["mode"] in ("T2", "T3")})
    key[iid] = {"prompt_id": r["prompt_id"], "provider": r["provider"], "model": r["model"]}
json.dump(items, open("label/items.json", "w"), ensure_ascii=False)
json.dump(key, open("label/key.json", "w"), indent=1)
print(len(items), "items")
