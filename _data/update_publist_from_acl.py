#!/usr/bin/env python3
"""Add the team members' ACL Anthology papers to _data/publist.yml.

Uses the `acl-anthology` package (pip install acl-anthology). For every team
member in _data/team_members.yml, the script finds them in the ACL Anthology
and, for every paper from --since (default 2025) on:

  * if the paper is already in publist.yml (fuzzy title match) and its url is
    missing or "to appear", fills in the Anthology url;
  * otherwise appends a new entry (title, full author list, year, Anthology
    url, venue) to the top of publist.yml.

ACL venue names are shortened ("EMNLP Findings", "ACL", ...) with the same
rules as update_publist_from_mq.py, whose publist.yml helpers this reuses.
Front matter (e.g. proceedings volumes a member edited) is skipped.

Members are looked up by name, also trying first + last and first + second
word ("Diego Molla Aliod" is "Diego Mollá" in the Anthology). If that is not
enough, add an `acl:` field with their Anthology person id (the last part of
https://aclanthology.org/people/<id>/) to team_members.yml.

The Anthology data (~250MB) is cloned into ~/.cache/acl-anthology on the
first run and updated on the next ones.

Usage:
    python _data/update_publist_from_acl.py --dry-run   # show what would change
    python _data/update_publist_from_acl.py             # update publist.yml
"""

import argparse
import sys
import warnings
from pathlib import Path

from acl_anthology import Anthology
from ruamel.yaml import YAML

from update_publist_from_mq import (MEMBERS, MISSING_URLS, PUBLIST, entry_url, find_match, new_entry, norm,
                                    set_entry_url, short_venue, shorten_display, split_entries)

ANTHOLOGY_DIR = Path.home() / ".cache" / "acl-anthology"


def find_people(anthology, member):
    """The Anthology people for a team member, by `acl:` id or by name."""
    if member.get("acl"):
        ids = member["acl"] if isinstance(member["acl"], list) else [member["acl"]]
        return [p for p in map(anthology.get_person, ids) if p]
    words = member["name"].split()
    variants = [(words[0], " ".join(words[1:])), (words[0], words[-1])] + ([(words[0], words[1])] if len(words) > 2 else [])
    for variant in variants:
        people = anthology.find_people(variant)
        if people:
            return people
    return []


def paper_details(paper):
    venue = paper.journal_title or paper.parent.title.as_text()
    return {
        "title": paper.title.as_text(),
        "url": paper.web_url,
        "authors": ", ".join(a.name.as_first_last() for a in paper.authors),
        "venue": short_venue(venue),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", type=int, default=2025, help="earliest year to consider (default: 2025)")
    ap.add_argument("--dry-run", action="store_true", help="print the changes without writing publist.yml")
    ap.add_argument("--member", action="append", help="only process members whose name contains this (repeatable)")
    ap.add_argument("--no-update", action="store_true", help="use the local Anthology copy without pulling updates")
    args = ap.parse_args()

    members = [m for m in YAML(typ="safe").load(MEMBERS.read_text())
               if m.get("acl") or m.get("scholar") or m.get("webpage")]
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

    print("Loading the ACL Anthology...", file=sys.stderr)
    warnings.filterwarnings("ignore", module="acl_anthology")  # name-resolution noise about other authors
    if args.no_update and (ANTHOLOGY_DIR / "data").exists():
        anthology = Anthology(datadir=ANTHOLOGY_DIR / "data")
    else:
        anthology = Anthology.from_repo(path=ANTHOLOGY_DIR, verbose=False)

    seen, added, url_updates = set(), [], []
    for member in members:
        people = find_people(anthology, member)
        print(f"== {member['name']} ({', '.join(p.id for p in people) or 'not found, skipping'})", file=sys.stderr)
        papers = [paper for person in people for paper in person.papers()
                  if int(paper.year) >= args.since and not paper.is_frontmatter]
        for paper in sorted(papers, key=lambda p: p.full_id):
            if paper.full_id in seen:
                continue
            seen.add(paper.full_id)
            d = paper_details(paper)
            i = find_match(d["title"], known)
            if i is None:
                added.append((int(paper.year), d))
                known.append(norm(d["title"]))  # catch near-duplicates later in the run
            elif i < len(chunks) and entry_url(chunks[i]).lower() in MISSING_URLS:
                chunks[i] = set_entry_url(chunks[i], d["url"])
                url_updates.append((publist[i]["title"], d["url"]))

    added.sort(key=lambda yd: -yd[0])
    print(f"\nVenues shortened ({len(venue_updates)}):")
    for old, new in venue_updates:
        print(f"  {old}\n    -> {new}")
    print(f"\nURLs filled in ({len(url_updates)}):")
    for t, u in url_updates:
        print(f"  {t}\n    -> {u}")
    print(f"\nNew papers ({len(added)}):")
    for y, d in added:
        print(f"  [{y}] {d['title']} -- {d['venue']}")

    if args.dry_run or not (added or url_updates or venue_updates):
        return
    out = header + "".join(new_entry(d, y) for y, d in added) + "".join(chunks)
    YAML(typ="safe").load(out)  # sanity check before overwriting
    PUBLIST.write_text(out)
    print(f"\nWrote {PUBLIST}")


if __name__ == "__main__":
    main()
