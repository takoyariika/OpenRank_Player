#!/usr/bin/env python3
"""OpenRank player synchronizer. Python stdlib only; run in a player's repo root."""
from __future__ import annotations
import datetime as dt
import json
import math
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PROTOCOL = "openrank/1"
REPO_RE = re.compile(r"[A-Za-z0-9-]{1,39}/[A-Za-z0-9_.-]{1,100}\Z")
GAME_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,62}\Z")
UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\Z")
BLOCK_RE = re.compile(r"```openrank-match\s*\n([^`]{1,2400})\n```", re.I)
API = "https://api.github.com"
K = 32


def api(path, token=None):
    req = urllib.request.Request(API + path, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "openrank-player/1",
        "X-GitHub-Api-Version": "2022-11-28",
        **({"Authorization": "Bearer " + token} if token else {}),
    })
    with urllib.request.urlopen(req, timeout=20) as res:
        return json.load(res)


def load_json(path, fallback):
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else fallback


def write_json(path, value):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    if not p.exists() or p.read_text(encoding="utf-8") != content:
        p.write_text(content, encoding="utf-8")
        return True
    return False


def parse_match(issue):
    if issue.get("pull_request") or not str(issue.get("title", "")).startswith("[OpenRank] "):
        return None
    match = BLOCK_RE.search(issue.get("body") or "")
    if not match:
        return None
    try:
        value = json.loads(match.group(1))
    except (ValueError, TypeError):
        return None
    if not isinstance(value, dict) or set(value) != {"protocol", "id", "game", "repos", "winner", "before", "played_at"}:
        return None
    ident = value["id"]
    if value["protocol"] != PROTOCOL or not isinstance(ident, str) or not UUID_RE.fullmatch(ident):
        return None
    if issue.get("title") != "[OpenRank] " + ident:
        return None
    if not isinstance(value["game"], str) or not GAME_RE.fullmatch(value["game"]):
        return None
    repos = value["repos"]
    if not isinstance(repos, list) or len(repos) != 2 or not all(isinstance(r, str) and REPO_RE.fullmatch(r) for r in repos):
        return None
    if repos != sorted(set(repos), key=str.lower) or repos[0].lower() == repos[1].lower():
        return None
    if value["winner"] not in repos or not isinstance(value["before"], dict) or set(value["before"]) != set(repos):
        return None
    if not all(type(v) is int and 0 <= v <= 100000 for v in value["before"].values()):
        return None
    if not isinstance(value["played_at"], str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value["played_at"]):
        return None
    try:
        dt.date.fromisoformat(value["played_at"])
    except ValueError:
        return None
    return value


def opponent_issue(match, own_repo, token, fetch=api):
    other = next(r for r in match["repos"] if r != own_repo)
    # Recently opened Issues are listed directly to avoid search-index delays.
    endpoints = [f"/repos/{other}/issues?state=all&per_page=100", 
                 "/search/issues?" + urllib.parse.urlencode({
                     "q": f'repo:{other} is:issue in:title "{match["id"]}"', "per_page": 30})]
    for path in endpoints:
        try:
            data = fetch(path, token)
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError) as exc:
            print("counterpart lookup unavailable:", str(exc), file=sys.stderr)
            continue
        issues = data if isinstance(data, list) else data.get("items", [])
        for issue in issues:
            parsed = parse_match(issue)
            if parsed == match and issue.get("user", {}).get("login", "").lower() == other.split("/")[0].lower():
                return issue
    return None


def delta_for_winner(match):
    winner = match["winner"]
    loser = next(r for r in match["repos"] if r != winner)
    a, b = match["before"][winner], match["before"][loser]
    expectation = 1 / (1 + 10 ** ((b - a) / 400))
    return math.floor(K * (1 - expectation) + 0.5)


def evaluate_stats(profile, ledger):
    games = {}
    for item in profile["games"]:
        games[item["id"]] = {"name": item["name"], "genre": item["genre"], "rp": 1500,
                              "wins": 0, "losses": 0, "matches": 0}
    for record in ledger:
        game = games.get(record["game"])
        if not game:
            continue
        if game["rp"] != record["before"]:
            raise ValueError(f"ledger mismatch for match {record['id']}")
        game["rp"] += record["delta"]
        game["wins" if record["won"] else "losses"] += 1
        game["matches"] += 1
    for game in games.values():
        game["win_rate"] = round(game["wins"] / game["matches"] * 100, 2) if game["matches"] else 0
    return games


def validate_profile(profile):
    assert isinstance(profile, dict) and isinstance(profile.get("games"), list), "profile.json: games must be a list"
    ids = set()
    for g in profile["games"]:
        assert isinstance(g, dict) and isinstance(g.get("id"), str) and GAME_RE.fullmatch(g["id"]), "invalid game id"
        assert isinstance(g.get("name"), str) and 0 < len(g["name"]) <= 100, "invalid game name"
        assert isinstance(g.get("genre"), str) and GAME_RE.fullmatch(g["genre"]), "invalid genre"
        assert g["id"] not in ids, "duplicate game id"
        ids.add(g["id"])


def sync(repo, token, fetch=api):
    profile = load_json("profile.json", {})
    validate_profile(profile)
    ledger = load_json("data/matches.json", [])
    if not isinstance(ledger, list):
        raise ValueError("data/matches.json must be a list")
    old_ids = {r["id"] for r in ledger}
    games = evaluate_stats(profile, ledger)
    own = repo.split("/")[0].lower()
    pending = []
    # Oldest first: sequential rating snapshots must be respected.
    issues = []
    for page in range(1, 11):
        batch = fetch(f"/repos/{repo}/issues?state=all&per_page=100&page={page}", token)
        issues.extend(batch)
        if len(batch) < 100:
            break
    for issue in reversed(issues):
        if issue.get("user", {}).get("login", "").lower() != own:
            continue
        match = parse_match(issue)
        if not match or repo not in match["repos"] or match["id"] in old_ids:
            continue
        if match["game"] not in games:
            pending.append({"id": match["id"], "status": "unknown-game"})
            continue
        peer = opponent_issue(match, repo, token, fetch)
        if peer is None:
            pending.append({"id": match["id"], "status": "awaiting-counterpart"})
            continue
        game = games[match["game"]]
        if game["rp"] != match["before"][repo]:
            pending.append({"id": match["id"], "status": "stale-rating"})
            continue
        gain = delta_for_winner(match)
        won = match["winner"] == repo
        record = {"id": match["id"], "game": match["game"], "opponent": next(r for r in match["repos"] if r != repo),
                  "winner": match["winner"], "before": game["rp"], "opponent_before": match["before"][next(r for r in match["repos"] if r != repo)],
                  "delta": gain if won else -gain, "won": won, "played_at": match["played_at"],
                  "own_issue": issue["html_url"], "opponent_issue": peer["html_url"]}
        ledger.append(record)
        old_ids.add(match["id"])
        game["rp"] += record["delta"]
        game["wins" if won else "losses"] += 1
        game["matches"] += 1
        print(f"Accepted {match['id']} ({match['game']}, {record['delta']:+})")
    games = evaluate_stats(profile, ledger)
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    owner, name = repo.split("/", 1)
    pages = f"https://{owner.lower()}.github.io/{name}/" if name.lower() != f"{owner.lower()}.github.io" else f"https://{name.lower()}/"
    manifest = {"protocol": PROTOCOL, "type": "player", "repository": repo,
                "display_name": profile.get("display_name") or owner, "page_url": pages,
                "games": games, "updated_at": now if ledger else "", "confirmed_count": len(ledger)}
    # Don't rewrite manifest on every no-op schedule tick.
    previous = load_json("manifest.json", {})
    if previous.get("games") == manifest["games"] and previous.get("repository") == repo and previous.get("display_name") == manifest["display_name"]:
        manifest["updated_at"] = previous.get("updated_at", "")
    write_json("data/matches.json", ledger)
    write_json("data/pending.json", pending)
    write_json("manifest.json", manifest)
    print(f"Synced {len(ledger)} confirmed matches; {len(pending)} pending")
    return manifest


if __name__ == "__main__":
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not REPO_RE.fullmatch(repo):
        sys.exit("GITHUB_REPOSITORY must be owner/repo")
    sync(repo, os.environ.get("GITHUB_TOKEN", ""))
