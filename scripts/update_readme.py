import os
import sys
import requests

USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER", "NITISH28111")
TOKEN = os.environ.get("GH_TOKEN")
README_PATH = "README.md"
START = "<!-- PROJECTS:START -->"
END = "<!-- PROJECTS:END -->"

headers = {"Accept": "application/vnd.github+json"}
if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"

def fetch_repos():
    repos = []
    page = 1
    while True:
        r = requests.get(
            f"https://api.github.com/users/{USERNAME}/repos",
            headers=headers,
            params={"per_page": 100, "page": page, "sort": "updated"},
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1
    # skip only the profile repo itself (username/username) — forks are included
    repos = [
        r for r in repos
        if r["name"].lower() != USERNAME.lower()
    ]
    return repos

def get_languages(repo):
    try:
        r = requests.get(repo["languages_url"], headers=headers)
        r.raise_for_status()
        langs = r.json()
        if langs:
            # sort by bytes of code, descending
            ordered = sorted(langs, key=langs.get, reverse=True)
            return ", ".join(ordered)
    except Exception:
        pass
    return repo.get("language") or "—"

def build_table(repos):
    if not repos:
        return "_No public repositories found._"

    header = "| Project | Description | Languages |\n|---|---|---|\n"
    rows = []
    for r in repos:
        name = r["name"]
        url = r["html_url"]
        desc = (r.get("description") or "—").replace("|", "-")
        langs = get_languages(r)
        rows.append(f"| **[{name}]({url})** | {desc} | `{langs}` |")
    return header + "\n".join(rows)

def update_readme(table_md):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if START not in content or END not in content:
        print("Markers not found in README.md — aborting.")
        sys.exit(1)

    before = content.split(START)[0]
    after = content.split(END)[1]
    new_content = f"{before}{START}\n{table_md}\n{END}{after}"

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    repos = fetch_repos()
    table = build_table(repos)
    update_readme(table)
    print(f"Updated README with {len(repos)} repos.")
