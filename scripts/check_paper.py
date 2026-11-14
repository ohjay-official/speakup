"""One-command check: rebuild every number from the raw replies and grades, rebuild the paper text,
and confirm it matches the committed paper word for word. Prints PASS or FAIL.

    python3 scripts/check_paper.py
"""
import json
import subprocess
import sys

paper = "report/paper_final.md"
committed = open(paper).read()
ok = True


def step(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(f"{'PASS' if cond else 'FAIL'}  {name}{('  ' + detail) if detail else ''}")


r1 = subprocess.run([sys.executable, "scripts/report_stats.py"], capture_output=True, text=True)
step("statistics rebuilt from raw replies and grades", r1.returncode == 0, r1.stderr[-300:])
r2 = subprocess.run([sys.executable, "scripts/assemble_paper.py", "--final"], capture_output=True, text=True)
step("paper text rebuilt from the statistics", r2.returncode == 0, r2.stderr[-300:])
rebuilt = open(paper).read()
open(paper, "w").write(committed)  # leave the committed file untouched
step("rebuilt paper matches the committed paper word for word", rebuilt == committed)
step("no [pending] markers left", "[pending" not in committed)

S = json.load(open("results/stats.json"))
q = S["main"]["Qwen3.8-27B|default"]
rb = S["robustness"]["Qwen3.8-27B"]
step("main arm sample sizes", S["main_n"] == {"Qwen3.8-27B": 698, "Gemini 3.5 Flash Lite": 720}, str(S["main_n"]))
print()
print("Headline results (Qwen3.8-27B, default system prompt):")
print(f"  advice: warned on {100 * rb['advice']['H']:.0f}% of frauds and {100 * rb['advice']['F']:.0f}% of legitimate products")
print(f"  task:   warned on {100 * q['fraud_T']:.0f}% of frauds, drop {100 * rb['supp']:.0f} points "
      f"(95% CI {100 * rb['supp_ci_scheme'][0]:.0f} to {100 * rb['supp_ci_scheme'][1]:.0f}), "
      f"McNemar {rb['mcnemar_one_pair']['advice_only']} vs {rb['mcnemar_one_pair']['task_only']}, p = {rb['mcnemar_one_pair']['p']:.1g}")
print(f"  fresh-conversation probe: frauds rated {S['probe']['Qwen3.8-27B']['probe_fraud_mean']:.0f}% likely fraud")
print()
print("PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
