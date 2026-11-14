import os, urllib.request, json
k = os.environ.get("NEBIUS_API_KEY", "")
print("matches dashboard key (start v1.CmQKH, end GRm6wD):", k.startswith("v1.CmQKH"), k.endswith("GRm6wD"))
print("end text found at position:", k.find("GRm6wD"), "of", len(k), "| also found case-insensitive at:", k.lower().find("grm6wd"))
print("length", len(k), "has_space_or_newline", any(c.isspace() for c in k), "has_quote", ('"' in k or "'" in k),
      "starts_serviceaccount", k.strip().lower().startswith("serviceaccount"), "starts_Bearer", k.strip().lower().startswith("bearer"),
      "dots", k.count("."), "nonascii", any(ord(c) > 127 for c in k))
for base in ("https://api.tokenfactory.nebius.com/v1/", "https://api.studio.nebius.com/v1/"):
    req = urllib.request.Request(base + "models", headers={"Authorization": "Bearer " + k.strip()})
    try:
        r = urllib.request.urlopen(req, timeout=30)
        d = json.load(r)
        ids = [m["id"] for m in d.get("data", [])]
        print(base, "OK", len(ids), ids)
    except Exception as e:
        print(base, "ERR", str(e)[:160])
