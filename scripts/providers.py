"""Minimal OpenAI-compatible chat client for the three free-tier providers.

Standard library only, so it runs on a bare GitHub Actions runner.
API keys come from environment variables set from GitHub secrets.
"""
import json
import os
import time
import urllib.error
import urllib.request

PROVIDERS = {
    "gemini": {
        "base": "https://generativelanguage.googleapis.com/v1beta/openai",
        "key_env": "GEMINI_API_KEY",
        "min_gap": 13.0,  # seconds between calls (about 5 a minute)
    },
    "groq": {
        "base": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY",
        "min_gap": 2.5,  # about 24 a minute, under the 30 cap
    },
    "cerebras": {
        "base": "https://api.cerebras.ai/v1",
        "key_env": "CEREBRAS_API_KEY",
        "min_gap": 2.5,
    },
}

_last_call = {}


def _request(url, key, body=None, timeout=120):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "speakup-eval/0.1",
        },
        method="POST" if body is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def list_models(provider):
    p = PROVIDERS[provider]
    key = os.environ.get(p["key_env"], "")
    if not key:
        return {"error": f"{p['key_env']} not set"}
    try:
        out = _request(f"{p['base']}/models", key)
        return {"models": sorted(m.get("id", "") for m in out.get("data", []))}
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:300]}"}
    except Exception as e:  # noqa: BLE001
        return {"error": repr(e)[:300]}


def chat(provider, model, messages, temperature=0.0, max_tokens=700, retries=5, min_gap=None, extra=None):
    """Return (text, meta). Waits to respect rate limits; retries on 429/5xx."""
    p = PROVIDERS[provider]
    key = os.environ[p["key_env"]]
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if extra:
        body.update(extra)
    mg = p["min_gap"] if min_gap is None else min_gap
    delay = mg
    slot = (provider, model)  # rate limits are per model
    for attempt in range(retries):
        gap = time.time() - _last_call.get(slot, 0)
        if gap < mg:
            time.sleep(mg - gap)
        _last_call[slot] = time.time()
        try:
            out = _request(f"{p['base']}/chat/completions", key, body)
            choice = out["choices"][0]
            text = (choice.get("message") or {}).get("content") or ""
            return text, {
                "finish_reason": choice.get("finish_reason"),
                "usage": out.get("usage"),
                "attempts": attempt + 1,
            }
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:1500]
            last = f"HTTP {e.code}: {msg}"
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(delay)
                delay = min(delay * 2, 120)
                continue
            return None, {"error": f"HTTP {e.code}: {msg}", "attempts": attempt + 1}
        except Exception as e:  # noqa: BLE001
            time.sleep(delay)
            delay = min(delay * 2, 120)
            last = repr(e)[:300]
    return None, {"error": f"gave up after {retries} attempts; last: {locals().get('last', '')[:1500]}", "attempts": retries}
