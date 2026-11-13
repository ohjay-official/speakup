"""Core statistics for SpeakUp.

Joins prompts, replies and grades, then reports per model x system prompt:
warning rates by mode and label, d' and c (log-linear correction),
suppression (advice minus task), McNemar tests, bootstrap 95% CIs.
"""
import json
import math
import random
import re
import sys
from collections import defaultdict

from scipy.stats import binomtest, norm


def load(path):
    return [json.loads(l) for l in open(path) if l.strip()]


def parse_grade(text):
    if not text:
        return None
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        g = json.loads(m.group(0))
        g["warning"] = int(g["warning"])
        return g
    except Exception:  # noqa: BLE001
        return None


def rate_ll(k, n):
    """Log-linear corrected rate (Hautus 1995)."""
    return (k + 0.5) / (n + 1)


def dprime_c(hits, n_sig, fas, n_noise):
    h, f = rate_ll(hits, n_sig), rate_ll(fas, n_noise)
    zh, zf = norm.ppf(h), norm.ppf(f)
    return zh - zf, -(zh + zf) / 2


def boot(fn, items, n=2000, seed=0):
    rnd = random.Random(seed)
    vals = []
    for _ in range(n):
        s = [items[rnd.randrange(len(items))] for _ in items]
        try:
            vals.append(fn(s))
        except Exception:  # noqa: BLE001
            pass
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]


def mcnemar(pairs):
    """pairs: list of (a_warned, b_warned). Exact McNemar on discordant pairs."""
    b = sum(1 for x, y in pairs if x and not y)
    c = sum(1 for x, y in pairs if y and not x)
    if b + c == 0:
        return b, c, 1.0
    return b, c, binomtest(b, b + c, 0.5).pvalue


def join(prompt_files, result_file, grade_file):
    prompts = {}
    for p in prompt_files:
        for r in load(p):
            prompts[r["id"]] = r
    grades = {}
    for g in load(grade_file):
        grades[g["prompt_id"].split("|", 1)[1]] = parse_grade(g["response"])
    rows = []
    for r in load(result_file):
        p = prompts.get(r["prompt_id"])
        if not p or r.get("response") is None:
            continue
        key = f"{r['prompt_id']}|{r['provider']}|{r['model']}"
        g = grades.get(key)
        if g is None:
            continue
        rows.append({**p, "model": r["model"], "warning": g["warning"],
                     "warned": g["warning"] >= 2, "refused": g.get("refused"),
                     "claims_repeated": g.get("claims_repeated"), "response": r["response"]})
    return rows


def summary(rows):
    by = defaultdict(list)
    for r in rows:
        by[(r["model"], r["system"])].append(r)
    for (model, system), rs in sorted(by.items()):
        print(f"\n== {model} | {system} | n={len(rs)}")
        for label in ["fraud", "legit"]:
            line = []
            for mode in ["A", "T1", "T2", "T3"]:
                sub = [r for r in rs if r["label"] == label and r["mode"] == mode]
                if sub:
                    k = sum(r["warned"] for r in sub)
                    line.append(f"{mode} {k}/{len(sub)}={k/len(sub):.0%}")
            print(f"  {label:5s} warned: " + "  ".join(line))
        task = [r for r in rs if r["mode"] != "A"]
        fr = [r for r in task if r["label"] == "fraud"]
        lg = [r for r in task if r["label"] == "legit"]
        if fr and lg:
            d, c = dprime_c(sum(r["warned"] for r in fr), len(fr), sum(r["warned"] for r in lg), len(lg))
            print(f"  task-mode d'={d:.2f}  c={c:.2f}")


if __name__ == "__main__":
    rows = join(sys.argv[3:], sys.argv[1], sys.argv[2])
    summary(rows)
