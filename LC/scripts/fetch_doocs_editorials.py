import os, csv, json, time, sys, re, urllib.request, urllib.parse

BAND_TSV = os.environ.get("BAND_TSV", "zerotrac-data/band_1700_1799_lctags.tsv")
OUT_DIR = os.environ.get("OUT_DIR", "editorials-data/band_1700_1799")
SUMMARY = os.environ.get("SUMMARY", "editorials-data/band_1700_1799_summary.tsv")
os.makedirs(OUT_DIR, exist_ok=True)

UA = {"User-Agent":"Mozilla/5.0 (Macintosh) AppleWebKit/537.36"}

def http_get(url, timeout=12):
    req = urllib.request.Request(url, headers=UA)
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, ""

def bucket_for(pid):
    lo = (pid // 100) * 100
    if lo == 0: lo = 1
    return f"{lo:04d}-{lo+99:04d}" if lo >= 100 else "0001-0099"

def try_direct(pid, title):
    """Construct exact URL from ID + title."""
    padded = f"{pid:04d}"
    safe_title = urllib.parse.quote(title)
    bucket = bucket_for(pid)
    url = f"https://raw.githubusercontent.com/doocs/leetcode/main/solution/{bucket}/{padded}.{safe_title}/README_EN.md"
    code, body = http_get(url)
    return code, body, url

def api_find(pid):
    """Fall back: list bucket via GitHub API, find folder starting with padded ID."""
    bucket = bucket_for(pid)
    api_url = f"https://api.github.com/repos/doocs/leetcode/contents/solution/{bucket}"
    code, body = http_get(api_url)
    if code != 200: return None
    try:
        items = json.loads(body)
        padded = f"{pid:04d}."
        for it in items:
            if it.get("name","").startswith(padded):
                folder = it["name"]
                # fetch README_EN
                raw = f"https://raw.githubusercontent.com/doocs/leetcode/main/solution/{bucket}/{urllib.parse.quote(folder)}/README_EN.md"
                c2, b2 = http_get(raw)
                if c2 == 200:
                    return raw, b2
        return None
    except Exception:
        return None

def parse_frontmatter_tags(md):
    m = re.search(r'^---\s*\n(.*?)\n---', md, re.DOTALL)
    if not m: return []
    fm = m.group(1)
    tags = re.findall(r'^\s*-\s+(.+)$', fm, re.MULTILINE)
    return [t.strip() for t in tags]

def parse_approaches(md):
    """Find approach headings — usually '### Solution 1: ...' format."""
    approaches = []
    # ### Solution N: Name
    for m in re.finditer(r'^###\s*Solution\s*\d+\s*:?\s*(.+?)$', md, re.MULTILINE):
        approaches.append(m.group(1).strip())
    # also try ## Approach N:
    if not approaches:
        for m in re.finditer(r'^##\s*Approach\s*\d+\s*:?\s*(.+?)$', md, re.MULTILINE):
            approaches.append(m.group(1).strip())
    return approaches

# Read band TSV
rows = []
with open(BAND_TSV) as f:
    r = csv.reader(f, delimiter="\t")
    next(r)
    for row in r:
        if len(row) < 9: continue
        rating, pid, title, slug, contest, qpos, diff, ar, tags = row
        try:
            pid_int = int(pid)
        except ValueError:
            continue
        rows.append((rating, pid_int, title, slug, qpos, ar, tags))

print(f"Total band problems: {len(rows)}", file=sys.stderr)

summary = []  # (slug, pid, title, status, doocs_tags, approaches, file)
hits, miss404, miss_api, errors = 0, 0, 0, 0

for i, (rating, pid, title, slug, qpos, ar, lc_tags) in enumerate(rows):
    status = "unknown"
    body = ""
    src_url = ""
    code, body, url = try_direct(pid, title)
    if code == 200:
        status = "direct"
        hits += 1
        src_url = url
    elif code == 404:
        # title might differ — try API
        res = api_find(pid)
        if res:
            src_url, body = res
            status = "api"
            hits += 1
            miss_api += 1
        else:
            status = "missing"
            miss404 += 1
    else:
        status = f"err_{code}"
        errors += 1

    doocs_tags = []
    approaches = []
    if status in ("direct","api") and body:
        doocs_tags = parse_frontmatter_tags(body)
        approaches = parse_approaches(body)
        # Save the editorial markdown
        fname = f"{pid:04d}_{slug}.md"
        with open(os.path.join(OUT_DIR, fname), "w") as o:
            o.write(body)
        summary.append((slug, pid, title, status, "|".join(doocs_tags), "|".join(approaches), fname, src_url))
    else:
        summary.append((slug, pid, title, status, "", "", "", ""))

    if (i+1) % 20 == 0:
        print(f"  {i+1}/{len(rows)} — hits {hits}, missing {miss404}, errors {errors}", file=sys.stderr)
    time.sleep(0.4)

with open(SUMMARY, "w") as o:
    o.write("Slug\tID\tTitle\tStatus\tDoocsTags\tApproaches\tFile\tSourceURL\n")
    for r in summary:
        o.write("\t".join(str(x) for x in r) + "\n")

print(f"\nDone. Hits: {hits}  Missing: {miss404}  Errors: {errors}", file=sys.stderr)
print(f"API fallback used: {miss_api}", file=sys.stderr)
print(f"Editorials saved: {OUT_DIR}", file=sys.stderr)
print(f"Summary: {SUMMARY}", file=sys.stderr)
