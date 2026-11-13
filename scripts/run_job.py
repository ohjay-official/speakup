"""Run one job described by a JSON file.

Job kinds:
  list_models  -> results/models.json
  chat         -> appends one JSON line per prompt to the output file;
                  prompts already in the output are skipped, so a job can be
                  re-run after a crash or a daily cap without repeating calls.

Job file fields for "chat":
  prompts:   path to a .jsonl of prompt records (id, messages, ...)
  targets:   list of {"provider": ..., "model": ...}
  output:    path to results .jsonl
  limit:     optional, max new calls per target this run
  time_budget_min: optional, stop cleanly before this many minutes
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from providers import PROVIDERS, chat, list_models  # noqa: E402


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def run_list_models(job):
    out = {p: list_models(p) for p in PROVIDERS}
    os.makedirs("results", exist_ok=True)
    with open("results/models.json", "w") as f:
        json.dump(out, f, indent=2)
    for p, v in out.items():
        print(p, "error" if "error" in v else f"{len(v['models'])} models", v.get("error", ""))


def run_chat(job):
    prompts = load_jsonl(job["prompts"])
    out_path = job["output"]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    done = {(r["prompt_id"], r["provider"], r["model"]) for r in load_jsonl(out_path)
            if r.get("response") is not None}
    start = time.time()
    budget = job.get("time_budget_min", 330) * 60
    limit = job.get("limit")
    with open(out_path, "a") as f:
        for t in job["targets"]:
            n = 0
            for p in prompts:
                if limit is not None and n >= limit:
                    break
                if time.time() - start > budget:
                    print("time budget reached, stopping")
                    return
                k = (p["id"], t["provider"], t["model"])
                if k in done:
                    continue
                text, meta = chat(t["provider"], t["model"], p["messages"],
                                  temperature=job.get("temperature", 0.0),
                                  max_tokens=job.get("max_tokens", 700))
                rec = {"prompt_id": p["id"], "provider": t["provider"], "model": t["model"],
                       "response": text, "meta": meta, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
                n += 1
                if text is None and "HTTP 4" in meta.get("error", "") and "429" not in meta.get("error", ""):
                    print("hard error, skipping target:", t, meta["error"])
                    break
            print(t, "new calls:", n)


if __name__ == "__main__":
    job = json.load(open(sys.argv[1]))
    {"list_models": run_list_models, "chat": run_chat}[job["kind"]](job)
