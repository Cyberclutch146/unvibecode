"""Check the Cohort 3 submission for changes.

Public data only; no token or Google login needed.

    python monitor.py
    python monitor.py --json

What it reports:
  * Issue #346 state, labels, comment count, and the latest comment.
  * Whether UnvibeCode has a release newer than 0.3.15.
  * Any newly filed issue that matches the submission's keywords.
  * The three newest commits on upstream main (for challenge/result updates).

Exit code is 0 when nothing needs attention, 1 when something changed.
"""

import json
import sys
import urllib.parse
import urllib.request

REPO = "FinanceFlash/unvibecode"
ISSUE = 346
BASELINE_VERSION = "0.3.15"
KEYWORDS = [
    "significant_production_source_files",
    "Material source coverage gate",
    "24/55",
    "test_settings.py",
    "testapp coverage",
]
# Issues already analysed and distinguished in section 9 of the submission.
KNOWN_DISTINCT = {50, 148, 201, 207, 219, 238, 241, 258, 331}


def get_json(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "unvibecode-monitor", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main():
    out = {}
    changes = []

    issue = get_json(f"https://api.github.com/repos/{REPO}/issues/{ISSUE}")
    comments = get_json(issue["comments_url"]) if issue["comments"] else []
    out["issue"] = {
        "number": issue["number"],
        "state": issue["state"],
        "labels": [l["name"] for l in issue["labels"]],
        "comments": issue["comments"],
        "updated_at": issue["updated_at"],
        "url": issue["html_url"],
    }
    if issue["state"] != "open":
        changes.append(f"issue is now {issue['state']}")
    if comments:
        last = comments[-1]
        out["latest_comment"] = {
            "author": last["user"]["login"],
            "created_at": last["created_at"],
            "body": last["body"][:400],
        }
        changes.append(f"new comment from {last['user']['login']}")
    else:
        out["latest_comment"] = None

    pypi = get_json("https://pypi.org/pypi/unvibecode/json")
    latest = pypi["info"]["version"]
    out["pypi"] = {
        "latest": latest,
        "baseline": BASELINE_VERSION,
        "changed": latest != BASELINE_VERSION,
    }
    if latest != BASELINE_VERSION:
        changes.append(f"new UnvibeCode release: {latest} (baseline {BASELINE_VERSION})")

    dupes = []
    known = []
    for kw in KEYWORDS:
        q = urllib.parse.quote(f'repo:{REPO} "{kw}"')
        try:
            res = get_json(f"https://api.github.com/search/issues?q={q}&per_page=10")
        except Exception:
            continue
        for item in res.get("items", []):
            if item["number"] == ISSUE:
                continue
            entry = {"number": item["number"], "title": item["title"], "keyword": kw}
            if item["number"] in KNOWN_DISTINCT:
                known.append(entry)
            else:
                dupes.append(entry)
    # de-duplicate by issue number
    seen = {}
    for d in dupes:
        seen.setdefault(d["number"], d)
    out["possible_duplicates"] = list(seen.values())
    seen_known = {}
    for d in known:
        seen_known.setdefault(d["number"], d)
    out["known_related"] = list(seen_known.values())
    if seen:
        changes.append(f"{len(seen)} new issue(s) match the submission keywords")

    commits = get_json(f"https://api.github.com/repos/{REPO}/commits?per_page=3")
    out["upstream_commits"] = [
        {
            "sha": c["sha"][:7],
            "date": c["commit"]["author"]["date"],
            "message": c["commit"]["message"].splitlines()[0],
        }
        for c in commits
    ]

    out["needs_attention"] = changes

    if "--json" in sys.argv:
        print(json.dumps(out, indent=2, ensure_ascii=True))
    else:
        i = out["issue"]
        print(f"Issue #{i['number']}: {i['state']} | comments={i['comments']} | labels={i['labels']}")
        print(f"  {i['url']}")
        if out["latest_comment"]:
            c = out["latest_comment"]
            print(f"  latest comment: {c['author']} at {c['created_at']}")
            print(f"  {c['body'][:300]}")
        else:
            print("  no comments yet")
        p = out["pypi"]
        flag = "CHANGED" if p["changed"] else "unchanged"
        print(f"PyPI: {p['latest']} ({flag}; baseline {p['baseline']})")
        if out["possible_duplicates"]:
            print("Possible duplicates:")
            for d in out["possible_duplicates"]:
                print(f"  #{d['number']} {d['title']}")
        else:
            print("Possible duplicates: none")
        if out.get("known_related"):
            print("Known related (already distinguished in section 9):")
            for d in out["known_related"]:
                print(f"  #{d['number']} {d['title'][:90]}")
        print("Newest upstream commits:")
        for c in out["upstream_commits"]:
            print(f"  {c['sha']} {c['date'][:10]} {c['message'][:80]}")
        print()
        if changes:
            print("NEEDS ATTENTION:")
            for c in changes:
                print(f"  - {c}")
        else:
            print("Nothing changed. No action needed.")

    return 1 if changes else 0


if __name__ == "__main__":
    raise SystemExit(main())
