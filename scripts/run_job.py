"""Run one job described by a JSON file.

Job kinds:
  list_models  -> results/models.json
  chat         -> appends one JSON line per prompt to the output file;
                  prompts already in the output are skipped, so a job can be
                  re-run after a crash or a daily cap without repeating calls.

Chat job fields (job level or per stage):
  prompts, output, targets [{provider, model, output?, shard?: [i, n], min_gap?}],
  limit, time_budget_min, temperature, max_tokens,
  pre: list of commands (argv lists) run before the stage, e.g. building grading prompts.

If LIVE_DIR is set, outputs are written under LIVE_DIR (outside the git work tree) so a
periodic `git pull --rebase` cannot swap the file out from under the writer. sync_live()
copies them back into the work tree.
"""
import json
import os
import shutil
import subprocess
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(__file__))
from providers import PROVIDERS, chat, list_models  # noqa: E402

LIVE = os.environ.get("LIVE_DIR")
_lock = threading.Lock()


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def live_path(path):
    if not LIVE:
        return path
    lp = os.path.join(LIVE, path)
    if not os.path.exists(lp):
        os.makedirs(os.path.dirname(lp), exist_ok=True)
        if os.path.exists(path):
            shutil.copy(path, lp)
    return lp


def sync_live():
    if not LIVE:
        return
    for root, _, files in os.walk(LIVE):
        for fn in files:
            src = os.path.join(root, fn)
            dst = os.path.relpath(src, LIVE)
            os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
            shutil.copy(src, dst)


def run_list_models(job):
    out = {p: list_models(p) for p in PROVIDERS}
    os.makedirs("results", exist_ok=True)
    with open("results/models.json", "w") as f:
        json.dump(out, f, indent=2)


def run_chat(job):
    """Each stage in order; inside a stage one thread per (provider, model, output)."""
    t0 = time.time()
    stages = job.get("stages") or [job]
    for i, st in enumerate(stages):
        full = {**job, **st}
        full.pop("stages", None)
        sync_live()
        for cmd in full.get("pre", []):
            print("pre:", cmd, flush=True)
            subprocess.run([sys.executable] + cmd, check=False)
        if not full.get("targets"):
            continue
        threads = [threading.Thread(target=_run_target, args=(full, t, t0)) for t in full["targets"]]
        for th in threads:
            th.start()
        for th in threads:
            th.join()
        sync_live()
        print(f"stage {i} done at {(time.time()-t0)/60:.1f} min", flush=True)


def _run_target(job, t, t0):
    prompts = load_jsonl(t.get("prompts", job.get("prompts")))
    out_path = live_path(t.get("output") or job["output"])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    done = {(r["prompt_id"], r["provider"], r["model"]) for r in load_jsonl(out_path)
            if r.get("response") is not None}
    budget = job.get("time_budget_min", 330) * 60
    limit = job.get("limit")
    shard = t.get("shard")
    n = fails = 0
    for idx, p in enumerate(prompts):
        if shard and idx % shard[1] != shard[0]:
            continue
        if limit is not None and n >= limit:
            break
        if time.time() - t0 > budget:
            print("time budget reached, stopping", t, flush=True)
            break
        if p.get("only_model") and p["only_model"] != t["model"]:
            continue
        k = (p["id"], t["provider"], t["model"])
        if k in done:
            continue
        text, meta = chat(t["provider"], t["model"], p["messages"],
                          temperature=job.get("temperature", 0.0),
                          max_tokens=job.get("max_tokens", 700), min_gap=t.get("min_gap"))
        rec = {"prompt_id": p["id"], "provider": t["provider"], "model": t["model"],
               "response": text, "meta": meta, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        with _lock:
            with open(out_path, "a") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        n += 1
        if text is None:
            fails += 1
            err = meta.get("error", "")
            if ("HTTP 4" in err and "429" not in err) or fails >= 25:
                print("stopping target after errors:", t, err, flush=True)
                break
    print(t, "new calls:", n, "failed:", fails, flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "--sync":
        sync_live()
        sys.exit(0)
    job = json.load(open(sys.argv[1]))
    {"list_models": run_list_models, "chat": run_chat}[job["kind"]](job)
