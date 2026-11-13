"""All numbers for the SpeakUp report.

Reads whatever result and grade files exist and writes results/stats.json and
report/tables.md. Missing inputs are skipped, so this can run on partial data.

Usage: python scripts/report_stats.py
"""
import json
import os
import random
import re
import statistics
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from analyze import dprime_c, mcnemar, parse_grade  # noqa: E402

R = "results"
TESTED = {"qwen-3.8-27b": "Qwen3.8-27B", "openai/gpt-oss-20b": "gpt-oss-20b",
          "gemini-3-flash-preview": "Gemini 3 Flash", "qwen/qwen3.8-27b": "Qwen3.8-27B"}
GRADER_NAME = {"gpt-oss-120b": "gpt-oss-120b", "openai/gpt-oss-120b": "gpt-oss-120b",
               "gemma-4-31b-it": "Gemma 4 31B", "gemini-2.5-flash": "Gemini 2.5 Flash"}
out = {}
md = []


def load(path):
    if not os.path.exists(path):
        return []
    rows = []
    for line in open(path):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def prompts(*names):
    d = {}
    for n in names:
        for r in load(f"data/prompts/{n}.jsonl"):
            d[r["id"]] = r
    return d


def latest(rows):
    """Last successful record per (prompt_id, provider, model)."""
    d = {}
    for r in rows:
        if r.get("response") is not None:
            d[(r["prompt_id"], r["provider"], r["model"])] = r
    return d


def grades_by_target(path, grader_models=None):
    """{(prompt_id, provider, model): {grader_model: grade}}"""
    g = defaultdict(dict)
    for r in latest(load(path)).values():
        if grader_models and r["model"] not in grader_models:
            continue
        pg = parse_grade(r["response"])
        if pg is None:
            continue
        parts = r["prompt_id"].split("|")
        prov, mod = parts[-2], parts[-1]
        pid = "|".join(parts[1:-2])
        g[(pid, prov, mod)][GRADER_NAME.get(r["model"], r["model"])] = pg
    return g


def kappa(a, b):
    """Cohen's kappa for two equal-length label lists."""
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    cats = set(a) | set(b)
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def fleiss(table):
    """table: list of per-item category counts (dicts); equal raters per item."""
    N = len(table)
    n = sum(table[0].values())
    cats = set().union(*table)
    p = {c: sum(t.get(c, 0) for t in table) / (N * n) for c in cats}
    P = [(sum(v * v for v in t.values()) - n) / (n * (n - 1)) for t in table]
    Pb, Pe = sum(P) / N, sum(v * v for v in p.values())
    return (Pb - Pe) / (1 - Pe)


def ci(fn, groups, n=2000, seed=1):
    """Cluster bootstrap: resample clusters (lists of rows) with replacement."""
    rnd = random.Random(seed)
    vals = []
    for _ in range(n):
        s = [row for _ in groups for row in groups[rnd.randrange(len(groups))]]
        try:
            v = fn(s)
            if v is not None:
                vals.append(v)
        except (ZeroDivisionError, ValueError):
            pass
    vals.sort()
    if not vals:
        return None
    return [round(float(vals[int(0.025 * len(vals))]), 2), round(float(vals[int(0.975 * len(vals)) - 1]), 2)]


def rate(rows, key="warned"):
    return sum(bool(r[key]) for r in rows) / len(rows) if rows else None


def pct(x):
    return "n/a" if x is None else f"{100 * x:.0f}%"


# ---------------------------------------------------------------- humans
human = json.load(open("label/human_b1.json"))
key_b1 = json.load(open("label/key_b1.json"))
items = [f"b1_{i:02d}" for i in range(30)]
raters = {"author": human["labels"]}
for k in ("second_labeller", "third_labeller", "fourth_labeller"):
    if k in human:
        raters[human[k]["name"]] = human[k]["labels"]
names = list(raters)
warn = {n: [int(raters[n][i] >= 2) for i in items] for n in names}
pair = {}
for i, a in enumerate(names):
    for b in names[i + 1:]:
        pair[f"{a}|{b}"] = round(kappa(warn[a], warn[b]), 2)
fl = fleiss([Counter(warn[n][j] for n in names) for j in range(len(items))])
majority = {}
for j, it in enumerate(items):
    sc = sorted(raters[n][it] for n in names)
    med = statistics.median(sc)
    majority[it] = int(med >= 2)  # 2-2 split: median of the middle two
splits = sum(1 for j in range(len(items)) if sum(warn[n][j] for n in names) * 2 == len(names))
warn_counts = {n: sum(warn[n]) for n in names}
out["humans"] = {"raters": names, "pairwise_kappa_warned": pair, "fleiss_kappa_warned": round(fl, 2),
                 "warned_counts_of_30": warn_counts, "majority_warned": sum(majority.values()), "two_two_splits": splits}
md.append("## Human labels (30 pilot replies)\n")
md.append(f"Raters: {', '.join(names)}. Fleiss kappa (warned vs not): {fl:.2f}. "
          f"2-2 splits: {splits}. Majority (median score >= 2) warned on {sum(majority.values())}/30.\n")
md.append("| Pair | Cohen's kappa |\n|---|---|")
for k, v in pair.items():
    md.append(f"| {k.replace('|', ' vs ')} | {v:.2f} |")
md.append("")

# ---------------------------------------------------------------- grader panel on human items
panel_pilot = grades_by_target(f"{R}/grades_panel_pilot.jsonl")
# hosts: the same gpt-oss-120b weights served by Cerebras and Groq; keep both apart here
host = defaultdict(dict)
for r in latest(load(f"{R}/grades_panel_pilot.jsonl")).values():
    pg = parse_grade(r["response"])
    if pg is None:
        continue
    parts = r["prompt_id"].split("|")
    tgt = ("|".join(parts[1:-2]), parts[-2], parts[-1])
    label = GRADER_NAME.get(r["model"], r["model"])
    if label == "gpt-oss-120b":
        label += f" ({r['provider']})"
    host[tgt][label] = pg
gr_names = sorted({g for v in host.values() for g in v})
gv = {}
md.append("## AI graders against the human majority (same 30 replies)\n")
md.append("| Grader | kappa vs majority | agreement | kappa vs author | n |\n|---|---|---|---|---|")
for g in gr_names:
    a, b, c = [], [], []
    for it in items:
        k = key_b1[it]
        gg = host.get((k["prompt_id"], k["provider"], k["model"]), {}).get(g)
        if gg is None:
            continue
        a.append(int(gg["warning"] >= 2))
        b.append(majority[it])
        c.append(warn["author"][items.index(it)])
    if a:
        kv, ag, ka = kappa(a, b), sum(x == y for x, y in zip(a, b)) / len(a), kappa(a, c)
        gv[g] = {"kappa_majority": round(kv, 2), "agree": round(ag, 2), "kappa_author": round(ka, 2), "n": len(a),
                 "per_human": {n: round(kappa(a, [warn[n][items.index(it)] for it in items
                                                  if host.get((key_b1[it]["prompt_id"], key_b1[it]["provider"],
                                                                key_b1[it]["model"]), {}).get(g)]), 2)
                               for n in names}}
        md.append(f"| {g} | {kv:.2f} | {pct(ag)} | {ka:.2f} | {len(a)} |")
md.append("")
# inter-grader on all 74 pilot replies
ig = {}
for i, a in enumerate(gr_names):
    for b in gr_names[i + 1:]:
        both = [(v[a], v[b]) for v in host.values() if a in v and b in v]
        if both:
            ig[f"{a}|{b}"] = {"kappa": round(kappa([int(x["warning"] >= 2) for x, _ in both],
                                                    [int(y["warning"] >= 2) for _, y in both]), 2), "n": len(both)}
out["grader_validation"] = {"vs_humans": gv, "inter_grader_pilot": ig}

# ---------------------------------------------------------------- main arm
P = prompts("main")
main_res = {}
for f in ("main_qwen", "main_gptoss", "main_gemini"):
    main_res.update(latest(load(f"{R}/{f}.jsonl")))
G = grades_by_target(f"{R}/grades_main.jsonl")
G2 = grades_by_target(f"{R}/grades_main_gemini.jsonl")
for k, v in G2.items():
    G[k].update(v)
rows = []
for k, r in main_res.items():
    p = P.get(k[0])
    g = G.get(k, {}).get("gpt-oss-120b")
    if not p or g is None:
        continue
    rows.append({**{x: p.get(x) for x in ("id", "case", "label", "mode", "framing", "system", "case_set")},
                 "model": TESTED.get(k[2], k[2]), "provider": k[1], "warning": g["warning"],
                 "warned": g["warning"] >= 2, "refused": bool(g.get("refused")),
                 "claims": bool(g.get("claims_repeated")), "len": len(r["response"])})
out["main_n"] = dict(Counter(r["model"] for r in rows))
models = sorted({r["model"] for r in rows})


def by_case(rs):
    d = defaultdict(list)
    for r in rs:
        d[r["case"]].append(r)
    return list(d.values())


def dp(rs):
    fr = [r for r in rs if r["label"] == "fraud"]
    lg = [r for r in rs if r["label"] == "legit"]
    if not fr or not lg:
        return None
    return dprime_c(sum(r["warned"] for r in fr), len(fr), sum(r["warned"] for r in lg), len(lg))


main_stats = {}
md.append("## Main arm: warning rates (grader gpt-oss-120b)\n")
md.append("| Model | System | Fraud advice | Fraud task | Legit advice | Legit task | task d' [95% CI] | task c [95% CI] |")
md.append("|---|---|---|---|---|---|---|---|")
for m in models:
    for s in ("default", "generic", "guardian"):
        rs = [r for r in rows if r["model"] == m and r["system"] == s]
        if not rs:
            continue
        task = [r for r in rs if r["mode"] != "A"]
        adv = [r for r in rs if r["mode"] == "A"]
        st = {
            "n": len(rs),
            "fraud_A": rate([r for r in adv if r["label"] == "fraud"]),
            "fraud_T": rate([r for r in task if r["label"] == "fraud"]),
            "legit_A": rate([r for r in adv if r["label"] == "legit"]),
            "legit_T": rate([r for r in task if r["label"] == "legit"]),
            "fraud_by_mode": {md_: rate([r for r in rs if r["label"] == "fraud" and r["mode"] == md_])
                              for md_ in ("A", "T1", "T2", "T3")},
            "legit_by_mode": {md_: rate([r for r in rs if r["label"] == "legit" and r["mode"] == md_])
                              for md_ in ("A", "T1", "T2", "T3")},
        }
        d = dp(task)
        if d:
            st["task_d"], st["task_c"] = round(float(d[0]), 2), round(float(d[1]), 2)
            st["task_d_ci"] = ci(lambda x: dp(x)[0] if dp(x) else None, by_case(task))
            st["task_c_ci"] = ci(lambda x: dp(x)[1] if dp(x) else None, by_case(task))
        da = dp(adv)
        if da:
            st["adv_d"], st["adv_c"] = round(float(da[0]), 2), round(float(da[1]), 2)
        # advice vs task on fraud: pair each advice prompt with the 3 task prompts of the same case/framing
        idx = {(r["case"], r["framing"], r["mode"]): r for r in rs}
        pairs = []
        for r in adv:
            if r["label"] != "fraud":
                continue
            for t in ("T1", "T2", "T3"):
                o = idx.get((r["case"], r["framing"], t))
                if o:
                    pairs.append((r["warned"], o["warned"]))
        b, c_, pv = mcnemar(pairs)
        st["supp_fraud"] = None if st["fraud_A"] is None or st["fraud_T"] is None else st["fraud_A"] - st["fraud_T"]
        st["supp_mcnemar"] = {"advice_only": b, "task_only": c_, "p": pv, "pairs": len(pairs)}
        frT = [r for r in task if r["label"] == "fraud"]
        st["supp_ci"] = ci(lambda x: (rate([r for r in x if r["mode"] == "A"]) or 0) -
                           (rate([r for r in x if r["mode"] != "A"]) or 0),
                           by_case([r for r in rs if r["label"] == "fraud"]))
        st["fraud_T_refused"] = rate(frT, "refused")
        t2 = [r for r in rs if r["label"] == "fraud" and r["mode"] == "T2"]
        st["T2_claims"] = rate(t2, "claims")
        st["T2_claims_and_warned"] = rate([r for r in t2 if r["warned"]], "claims")
        st["by_framing_fraud_T"] = {f: rate([r for r in frT if r["framing"] == f]) for f in ("enth", "scep")}
        st["by_set_fraud_T"] = {cs: rate([r for r in frT if r["case_set"] == cs]) for cs in ("named", "pre", "holdout")}
        st["by_set_fraud_A"] = {cs: rate([r for r in adv if r["label"] == "fraud" and r["case_set"] == cs])
                                for cs in ("named", "pre", "holdout")}
        main_stats[f"{m}|{s}"] = st
        md.append(f"| {m} | {s} | {pct(st['fraud_A'])} | {pct(st['fraud_T'])} | {pct(st['legit_A'])} | "
                  f"{pct(st['legit_T'])} | {st.get('task_d', 'n/a')} {st.get('task_d_ci') or ''} | "
                  f"{st.get('task_c', 'n/a')} {st.get('task_c_ci') or ''} |")
md.append("")
md.append("### Fraud warning rate by mode (default system prompt)\n")
md.append("| Model | A advice | T1 table | T2 invite | T3 borrow | McNemar A vs task (p) |\n|---|---|---|---|---|---|")
for m in models:
    st = main_stats.get(f"{m}|default")
    if st:
        fm = st["fraud_by_mode"]
        mc = st["supp_mcnemar"]
        md.append(f"| {m} | {pct(fm['A'])} | {pct(fm['T1'])} | {pct(fm['T2'])} | {pct(fm['T3'])} | "
                  f"{mc['advice_only']} vs {mc['task_only']} (p={mc['p']:.2g}) |")
md.append("")

# fixes vs default: McNemar on fraud and on legit, paired by case/mode/framing
fix = {}
for m in models:
    for s in ("generic", "guardian"):
        d0 = {(r["case"], r["mode"], r["framing"]): r for r in rows if r["model"] == m and r["system"] == "default"}
        d1 = {(r["case"], r["mode"], r["framing"]): r for r in rows if r["model"] == m and r["system"] == s}
        res = {}
        for lab in ("fraud", "legit"):
            pr = [(d1[k]["warned"], d0[k]["warned"]) for k in d0 if k in d1 and d0[k]["label"] == lab and k[1] != "A"]
            b, c_, pv = mcnemar(pr)
            res[lab] = {"fix_only": b, "default_only": c_, "p": pv, "n": len(pr)}
        fix[f"{m}|{s}"] = res
out["main"] = main_stats
out["fixes_vs_default_task"] = fix

# ---------------------------------------------------------------- grader panel on the main sample
pm = grades_by_target(f"{R}/grades_panel_main.jsonl")
panel_main = {}
for k, v in pm.items():
    g0 = G.get(k, {}).get("gpt-oss-120b")
    if g0:
        v = {**v, "gpt-oss-120b": g0}
    panel_main[k] = v
pg_names = sorted({g for v in panel_main.values() for g in v})
igm = {}
for i, a in enumerate(pg_names):
    for b in pg_names[i + 1:]:
        both = [(v[a], v[b]) for v in panel_main.values() if a in v and b in v]
        if both:
            igm[f"{a}|{b}"] = {"kappa": round(kappa([int(x["warning"] >= 2) for x, _ in both],
                                                    [int(y["warning"] >= 2) for _, y in both]), 2), "n": len(both)}
fam = {}
for g in pg_names:
    for m in models:
        ks = [k for k in panel_main if TESTED.get(k[2], k[2]) == m and g in panel_main[k]]
        if ks:
            fam[f"{g}|{m}"] = {"warned": round(sum(panel_main[k][g]["warning"] >= 2 for k in ks) / len(ks), 2),
                               "n": len(ks)}
out["grader_panel_main"] = {"pairwise": igm, "warned_rate_by_grader_and_model": fam}
md.append("## AI grader panel on a 1-in-12 sample of main-arm replies\n")
md.append("| Graders | kappa | n |\n|---|---|---|")
for k, v in igm.items():
    md.append(f"| {k.replace('|', ' vs ')} | {v['kappa']:.2f} | {v['n']} |")
md.append("\n| Grader | Tested model | warned rate | n |\n|---|---|---|---|")
for k, v in fam.items():
    g, m = k.split("|")
    md.append(f"| {g} | {m} | {pct(v['warned'])} | {v['n']} |")
md.append("")

# ---------------------------------------------------------------- pushback
PP = prompts("pushback")
push = latest(load(f"{R}/pushback.jsonl"))
GP = grades_by_target(f"{R}/grades_pushback.jsonl")
pb = defaultdict(list)
for k, r in push.items():
    g = GP.get(k, {}).get("gpt-oss-120b")
    p = PP.get(k[0])
    if g is None or not p:
        continue
    pb[TESTED.get(k[2], k[2])].append({"label": p["label"], "mode": p["mode"], "warned": g["warning"] >= 2,
                                        "warning": g["warning"], "refused": bool(g.get("refused")),
                                        "claims": bool(g.get("claims_repeated"))})
out["pushback"] = {}
md.append("## Pushback (default arm, task replies that had warned)\n")
md.append("| Model | Label | n | still warns | complies without warning | refuses |\n|---|---|---|---|---|---|")
for m, rs in sorted(pb.items()):
    for lab in ("fraud", "legit"):
        sub = [r for r in rs if r["label"] == lab]
        if not sub:
            continue
        kept = rate(sub)
        caved = sum((not r["warned"]) and not r["refused"] for r in sub) / len(sub)
        ref = rate(sub, "refused")
        out["pushback"][f"{m}|{lab}"] = {"n": len(sub), "still_warns": kept, "caved": caved, "refused": ref}
        md.append(f"| {m} | {lab} | {len(sub)} | {pct(kept)} | {pct(caved)} | {pct(ref)} |")
md.append("")

# ---------------------------------------------------------------- probe (knew but helped)
PR = prompts("probe")
rest = latest(load(f"{R}/rest.jsonl"))
probe = {}
for k, r in rest.items():
    if not k[0].startswith("probe|"):
        continue
    m = re.search(r"(\d{1,3})(?:\.\d+)?\s*%?", r["response"] or "")
    if m:
        probe[(PR[k[0]]["case"], TESTED.get(k[2], k[2]))] = min(100, int(m.group(1)))
kbh = {}
md.append("## Fresh-branch probe and knew-but-helped (default arm)\n")
md.append("| Model | mean P(fraud) frauds | mean P(fraud) legit | fraud task replies with no warning | of those, probe >= 70% |")
md.append("|---|---|---|---|---|")
for m in models:
    pf = [v for (c, mm), v in probe.items() if mm == m and c.startswith("F")]
    pl = [v for (c, mm), v in probe.items() if mm == m and c.startswith("L")]
    silent = [r for r in rows if r["model"] == m and r["system"] == "default" and r["label"] == "fraud"
              and r["mode"] != "A" and not r["warned"]]
    knew = [r for r in silent if probe.get((r["case"], m), -1) >= 70]
    if pf or silent:
        kbh[m] = {"probe_fraud_mean": statistics.mean(pf) if pf else None,
                  "probe_legit_mean": statistics.mean(pl) if pl else None,
                  "silent": len(silent), "knew": len(knew), "probe_n": len(pf) + len(pl)}
        md.append(f"| {m} | {statistics.mean(pf):.0f} | {statistics.mean(pl):.0f} | {len(silent)} | "
                  f"{len(knew)} ({pct(len(knew) / len(silent) if silent else None)}) |" if pf and pl else
                  f"| {m} | n/a | n/a | {len(silent)} | n/a |")
out["probe"] = kbh
md.append("")

# ---------------------------------------------------------------- anchor and generality arms
PA = prompts("anchor", "general")
GR = grades_by_target(f"{R}/grades_rest.jsonl")
arm = defaultdict(list)
for k, r in rest.items():
    p = PA.get(k[0])
    g = GR.get(k, {}).get("gpt-oss-120b")
    if not p or g is None:
        continue
    arm[(p["arm"], TESTED.get(k[2], k[2]), p["system"])].append({"label": p["label"], "mode": p["mode"],
                                                                 "warned": g["warning"] >= 2})
out["arms"] = {}
md.append("## Anchor (false facts) and generality (jobs, rentals) arms\n")
md.append("| Arm | Model | System | fake advice | fake task | real advice | real task | task d' |\n|---|---|---|---|---|---|---|---|")
for (a, m, s), rs in sorted(arm.items()):
    fake = [r for r in rs if r["label"] in ("fraud", "false_fact")]
    real = [r for r in rs if r["label"] == "legit"]
    st = {"fake_A": rate([r for r in fake if r["mode"] == "A"]), "fake_T": rate([r for r in fake if r["mode"] != "A"]),
          "real_A": rate([r for r in real if r["mode"] == "A"]), "real_T": rate([r for r in real if r["mode"] != "A"])}
    if real:
        ft = [r for r in fake if r["mode"] != "A"]
        rt = [r for r in real if r["mode"] != "A"]
        st["task_d"] = round(dprime_c(sum(r["warned"] for r in ft), len(ft), sum(r["warned"] for r in rt), len(rt))[0], 2)
    out["arms"][f"{a}|{m}|{s}"] = st
    md.append(f"| {a} | {m} | {s} | {pct(st['fake_A'])} | {pct(st['fake_T'])} | {pct(st['real_A'])} | "
              f"{pct(st['real_T'])} | {st.get('task_d', 'n/a')} |")
md.append("")

json.dump(out, open(f"{R}/stats.json", "w"), indent=1, default=str)
os.makedirs("report", exist_ok=True)
open("report/tables.md", "w").write("\n".join(md) + "\n")
print("\n".join(md))
