#!/usr/bin/env python3
"""Sync _data/publist.yml with the team members' Macquarie researcher pages.

For every team member with a `webpage:` link (their page on
https://researchers.mq.edu.au) in _data/team_members.yml, the script reads
their publication list and, for every paper from --since (default 2025) on:

  * if the paper is already in publist.yml (fuzzy title match) and its url is
    missing or "to appear", fills in the url;
  * otherwise appends a new entry (title, authors, year, url, venue) to the
    top of publist.yml.

Papers are de-duplicated across members and against the existing list.
Preprints and working papers are skipped unless --include-preprints.

The url is the paper's DOI when the portal has one, otherwise its portal page.
The portal only gives author initials ("M. Dras"). The DOIs are cached in
~/.cache/update_publist.json.

publist.yml is edited as text, so the existing entries keep their formatting.

The portal's HTML pages are behind a Cloudflare check, so the publication
list is read from its RSS version (<webpage>/publications/?format=rss).

Usage:
    python _data/update_publist.py --dry-run   # show what would change
    python _data/update_publist.py             # update publist.yml
"""

import argparse
import difflib
import html
import json
import re
import sys
import time
from pathlib import Path

import requests
from ruamel.yaml import YAML

DATA_DIR = Path(__file__).resolve().parent
PUBLIST = DATA_DIR / "publist.yml"
MEMBERS = DATA_DIR / "team_members.yml"
CACHE = Path.home() / ".cache" / "update_publist.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
DELAY = 1.0
MAX_PAGES = 20
MISSING_URLS = {"", "to appear", "tba", "#", "none", "null"}
TITLE_SIMILARITY = 0.9
PREPRINT_VENUES = ("arxiv", "ssrn", "preprint", "biorxiv", "medrxiv", "research square")


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


# ---------------------------------------------------------------- macquarie portal
#
# Papers are yielded as dicts with title, year, venue, preprint and `details`,
# a callable returning {title, url, authors, venue}, so the extra request for
# the DOI is only made when a paper is new or lacks a url.

def get(session, url):
    """GET a portal page; None on any failure."""
    time.sleep(DELAY)
    try:
        r = session.get(url, headers=HEADERS, timeout=30)
    except requests.RequestException:
        return None
    return r.text if r.status_code == 200 else None


def authors(s):
    """'Maskey, U. A. Y., Dras, M. & Naseem, U.' -> 'U. A. Y. Maskey, M. Dras, U. Naseem'."""
    s = strip_tags(s).replace(" & ", ", ").strip(" ,")
    names = re.findall(r"([^,]+?),\s*((?:[^\s,]+\.\s*)+)(?:,|$)", s)
    return ", ".join(f"{initials.strip()} {last.strip()}" for last, initials in names) or s


def papers(session, member, since, cache):
    feed_url = member["webpage"].rstrip("/") + "/publications/"
    for page in range(MAX_PAGES):
        feed = get(session, f"{feed_url}?page={page}&format=rss")
        if feed is None:
            print(f"   could not read {feed_url}, skipping", file=sys.stderr)
            return
        recent = False
        for item in re.findall(r"<item>(.*?)</item>", feed, re.S):
            year = re.search(r"<dc:date>(\d{4})", item)
            if not year or int(year.group(1)) < since:
                continue
            recent = True
            desc = html.unescape(re.search(r"<description>(.*?)</description>", item, re.S).group(1))
            title = strip_tags(re.search(r'<h3 class="title">(.*?)</h3>', desc, re.S).group(1))
            link = strip_tags(re.search(r"<link>(.*?)</link>", item).group(1))
            names = desc.split("</h3>", 1)[1].split('<span class="date">', 1)[0]
            venue = re.search(r'<em>(.*?)</em>|<span class="journal">In: (.*?)</span></span>', desc, re.S)
            venue = strip_tags(venue.group(1) or venue.group(2)).rstrip(".") if venue else ""
            kind = strip_tags(re.search(r'<p class="type">(.*?)</p>', desc, re.S).group(1))
            d = {"title": title, "url": link, "authors": authors(names), "venue": short_venue(venue)}
            yield {"title": title, "year": int(year.group(1)), "venue": venue,
                   "preprint": "Preprint" in kind or "Working paper" in kind,
                   "details": lambda d=d: {**d, "url": doi(session, d["url"], cache) or d["url"]}}
        if not recent:  # the feed is newest first
            return


def doi(session, link, cache):
    key = "mq:" + link
    if key not in cache:
        page = get(session, link)
        if page is None:
            return None
        m = re.search(r'href="(https?://(?:dx\.)?doi\.org/[^"]+)"', page)
        cache[key] = html.unescape(m.group(1)) if m else None
    return cache[key]


def is_preprint(venue):
    return any(p in venue.lower() for p in PREPRINT_VENUES)


# ACL venues, checked in order (IJCNLP-AACL before AACL, NAACL/EACL/TACL before ACL),
# as (short name, patterns).
ACL_VENUES = [
    ("IJCNLP-AACL", r"(?=.*(international joint conference on natural language processing|\bIJCNLP\b))"
                    r"(?=.*(asia-pacific chapter of the association|\bAACL\b))"),
    ("AACL", r"asia-pacific chapter of the association|\bAACL\b"),
    ("COLING", r"international conference on computational linguistics|\bCOLING\b"),
    ("EMNLP", r"empirical methods in natural language processing|\bEMNLP\b"),
    ("NAACL", r"(north american|nations of the americas) chapter of the association|\bNAACL\b"),
    ("EACL", r"european chapter of the association|\bEACL\b"),
    ("TACL", r"transactions of the association for computational linguistics|\bTACL\b"),
    ("ACL", r"annual meeting of the association for computational linguistics|\bACL\b"),
]


def short_venue(venue):
    """'Findings of the Association for Computational Linguistics: EACL 2026' -> 'EACL Findings'.

    Workshops and non-ACL venues are returned unchanged.
    """
    if re.search(r"workshop", venue, re.I):
        return venue
    for short, pattern in ACL_VENUES:
        if re.search(pattern, venue, re.I):
            if short != "TACL" and re.search(r"\bfindings\b", venue, re.I):
                return f"{short} Findings"
            if re.search(r"industry track", venue, re.I):
                return f"{short} Industry Track"
            if re.search(r"system demonstrations|demo track", venue, re.I):
                return f"{short} Demo Track"
            return short
    return venue


# ---------------------------------------------------------------- publist

def norm(title):
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def find_match(title, known):
    """Index of the entry in `known` (list of normalised titles) matching `title`."""
    t = norm(title)
    for i, k in enumerate(known):
        if k == t or difflib.SequenceMatcher(None, k, t).ratio() >= TITLE_SIMILARITY:
            return i
    return None


def split_entries(text):
    """Split publist.yml into a header and one text chunk per `- title:` entry."""
    parts = re.split(r"(?m)^(?=- title:)", text)
    return parts[0], parts[1:]


URL_LINE = re.compile(r"(?m)^(\s+url:)[ \t]*(.*?)[ \t]*$")


def entry_url(chunk):
    m = URL_LINE.search(chunk)
    return m.group(2).strip().strip("'\"") if m else ""


def set_entry_url(chunk, url):
    return URL_LINE.sub(lambda m: f"{m.group(1)} {url}", chunk, count=1)


DISPLAY_LINE = re.compile(r"(?m)^(\s+display:)[ \t]*(.*?)[ \t]*$")


def shorten_display(chunk):
    """Shorten the entry's ACL venue name; returns (chunk, old, new) or (chunk, None, None)."""
    m = DISPLAY_LINE.search(chunk)
    if not m:
        return chunk, None, None
    old = m.group(2)
    old = json.loads(old) if old.startswith('"') else old.strip("'")
    new = short_venue(old)
    if new == old.strip():
        return chunk, None, None
    return DISPLAY_LINE.sub(lambda m: f"{m.group(1)} {q(new)}", chunk, count=1), old, new


def q(s):
    return json.dumps(s, ensure_ascii=False)  # a JSON string is a valid YAML scalar


def new_entry(d, year):
    return (f"- title: {q(d['title'])}\n"
            f"  authors: {q(d['authors'])}\n"
            f"  year: {year}\n"
            f"  link:\n"
            f"    url: {d['url'] or 'to appear'}\n"
            f"    display: {q(d['venue'])}\n"
            f"  highlight: 0\n\n")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", type=int, default=2025, help="earliest year to consider (default: 2025)")
    ap.add_argument("--dry-run", action="store_true", help="print the changes without writing publist.yml")
    ap.add_argument("--include-preprints", action="store_true", help="also add preprints and working papers")
    ap.add_argument("--member", action="append", help="only process members whose name contains this (repeatable)")
    args = ap.parse_args()

    members = [m for m in YAML(typ="safe").load(MEMBERS.read_text()) if m.get("webpage")]
    if args.member:
        members = [m for m in members if any(s.lower() in m["name"].lower() for s in args.member)]

    text = PUBLIST.read_text()
    header, chunks = split_entries(text)
    publist = YAML(typ="safe").load(text) or []
    assert len(publist) == len(chunks), "could not split publist.yml into entries"
    known = [norm(str(p.get("title", ""))) for p in publist]

    venue_updates = []
    for i, chunk in enumerate(chunks):
        chunks[i], old, new = shorten_display(chunk)
        if new:
            venue_updates.append((old, new))

    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    session = requests.Session()
    seen, added, url_updates, skipped = set(), [], [], []

    try:
        for member in members:
            print(f"== {member['name']}", file=sys.stderr)
            for p in papers(session, member, args.since, cache):
                key = norm(p["title"])
                if key in seen:
                    continue
                seen.add(key)
                i = find_match(p["title"], known)
                if i is not None:
                    if i < len(chunks) and entry_url(chunks[i]).lower() in MISSING_URLS:
                        d = p["details"]()
                        if d["url"]:
                            chunks[i] = set_entry_url(chunks[i], d["url"])
                            url_updates.append((publist[i]["title"], d["url"]))
                elif not args.include_preprints and (p["preprint"] or is_preprint(p["venue"])):
                    skipped.append(p["title"])
                else:
                    added.append((p["year"], p["details"]()))
                    known.append(key)  # catch near-duplicates later in the run
    except KeyboardInterrupt:
        print("\n!! Interrupted, saving progress so far.", file=sys.stderr)
    finally:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(cache, indent=1, ensure_ascii=False))

    added.sort(key=lambda yd: -yd[0])
    print(f"\nVenues shortened ({len(venue_updates)}):")
    for old, new in venue_updates:
        print(f"  {old}\n    -> {new}")
    print(f"\nURLs filled in ({len(url_updates)}):")
    for t, u in url_updates:
        print(f"  {t}\n    -> {u}")
    print(f"\nNew papers ({len(added)}):")
    for y, d in added:
        print(f"  [{y}] {d['title']} -- {d['venue'] or '?'}")
    if skipped:
        print(f"\nSkipped preprints ({len(skipped)}), use --include-preprints to add them:")
        for t in skipped:
            print(f"  {t}")

    if args.dry_run or not (added or url_updates or venue_updates):
        return
    out = header + "".join(new_entry(d, y) for y, d in added) + "".join(chunks)
    YAML(typ="safe").load(out)  # sanity check before overwriting
    PUBLIST.write_text(out)
    print(f"\nWrote {PUBLIST}")


if __name__ == "__main__":
    main()
