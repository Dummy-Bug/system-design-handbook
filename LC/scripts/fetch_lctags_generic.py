import json, sys, time, urllib.request
infile, outfile = sys.argv[1], sys.argv[2]
rows = [l.rstrip("\n").split("\t")[:6] for l in open(infile) if l.strip()]
q = """query q($t:String!){question(titleSlug:$t){difficulty stats topicTags{name}}}"""
with open(outfile, "w") as out:
    out.write("Rating\tID\tTitle\tSlug\tContest\tQPos\tDifficulty\tAR\tLCtags\n")
    for i, r in enumerate(rows):
        if len(r) < 6: continue
        rating, pid, title, slug, contest, qpos = r
        body = json.dumps({"query": q, "variables": {"t": slug}}).encode()
        req = urllib.request.Request("https://leetcode.com/graphql", data=body, method="POST",
            headers={"Content-Type":"application/json","User-Agent":"Mozilla/5.0"})
        try:
            d = json.loads(urllib.request.urlopen(req, timeout=12).read())
            q_ = d.get("data",{}).get("question") or {}
            diff = q_.get("difficulty","")
            stats = json.loads(q_.get("stats","{}")) if q_.get("stats") else {}
            ar = stats.get("acRate","")
            tags = ",".join([t["name"] for t in (q_.get("topicTags") or [])])
        except Exception as e:
            diff, ar, tags = "ERR", "ERR", f"ERR:{e}"
        out.write(f"{rating}\t{pid}\t{title}\t{slug}\t{contest}\t{qpos}\t{diff}\t{ar}\t{tags}\n")
        out.flush()
        if i % 20 == 0: print(f"{i+1}/{len(rows)}", file=sys.stderr)
        time.sleep(0.5)
