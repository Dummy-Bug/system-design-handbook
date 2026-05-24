import os, json, sys

cache_dir = sys.argv[1]
ratings_tsv = sys.argv[2]
band_min = int(sys.argv[3])
band_max = int(sys.argv[4])

# Load ratings
problems = {}
with open(ratings_tsv) as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) < 7: continue
        try:
            rating = float(parts[0])
        except: continue
        if band_min <= rating < band_max:
            slug = parts[4]
            problems[slug] = {'rating': rating, 'id': parts[1], 'title': parts[2]}

print(f"Rating|ID|Title|Content", flush=True)
for slug, meta in sorted(problems.items(), key=lambda x: float(x[1]['rating'])):
    fpath = os.path.join(cache_dir, slug + '.json')
    content = ''
    if os.path.exists(fpath):
        try:
            data = json.load(open(fpath))
            q = data.get('data', {}).get('question') or {}
            raw = q.get('content') or ''
            # strip HTML tags
            import re
            raw = re.sub(r'<[^>]+>', ' ', raw)
            raw = re.sub(r'\s+', ' ', raw).strip()
            content = raw[:500]
        except: pass
    print(f"{meta['rating']}|{meta['id']}|{meta['title']}|{content}", flush=True)
