#!/usr/bin/env python3
"""Tracker — the story's project, complete. (The worked example; rebuild yours via the chapters.)

Born Chapter 1 (skeleton + add), hardened Chapter 2 (quotes + atomic writes),
completed Chapters 4/8 (close, tag, search). stdlib only.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

VERSION = "1.0.1"
DATA = Path(os.environ.get("TRACKER_DATA", Path(__file__).parent / "tasks.json"))
USAGE = """usage: tracker.py <command> [args]
  add <text...>      add a task (multi-word and quotes safe); #tag tokens become tags
  close <id>         mark a task done
  tag <id> <tag>     add a tag to a task
  list               list all tasks
  search <text...>   find tasks by text or tag (case-insensitive)
  version            print the version"""


def load():
    try:
        return json.loads(DATA.read_text())
    except FileNotFoundError:
        return {"next_id": 1, "tasks": []}
    except json.JSONDecodeError:
        # Chapter 2's law: never destroy corrupt data — back it up (never overwrite
        # an earlier backup), start clean.
        n = 1
        backup = DATA.with_name(f"{DATA.stem}.corrupt.json")
        while backup.exists():
            backup = DATA.with_name(f"{DATA.stem}.corrupt-{n}.json")
            n += 1
        DATA.replace(backup)
        print(f"warning: {DATA.name} was corrupt; backed up to {backup.name}", file=sys.stderr)
        return {"next_id": 1, "tasks": []}


def save(data):
    # Chapter 2's law: atomic writes — a failed write must never truncate real data.
    fd, tmp = tempfile.mkstemp(dir=str(DATA.parent))
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=1)
        os.replace(tmp, DATA)
    except BaseException:
        os.unlink(tmp)
        raise


def _split_tags(words):
    """Chapter 8: '#infra' tokens are tags; the rest is the task text."""
    tags = [w.lstrip("#").lower() for w in words if w.startswith("#")]
    text = " ".join(w for w in words if not w.startswith("#"))
    return text, tags


def cmd_add(words):
    text, tags = _split_tags(words)
    if not text:
        sys.exit("add: need task text")
    data = load()
    tid = data["next_id"]
    data["next_id"] += 1
    data["tasks"].append({"id": tid, "text": text, "status": "open", "tags": sorted(set(tags))})
    save(data)
    print(tid)


def cmd_close(tid):
    data = load()
    for t in data["tasks"]:
        if t["id"] == tid:
            t["status"] = "done"
            save(data)
            return
    sys.exit(f"close: no task {tid}")


def cmd_tag(tid, tag):
    data = load()
    for t in data["tasks"]:
        if t["id"] == tid:
            t["tags"] = sorted(set(t["tags"] + [tag.lstrip("#").lower()]))
            save(data)
            return
    sys.exit(f"tag: no task {tid}")


def cmd_list():
    for t in load()["tasks"]:
        mark = "x" if t["status"] == "done" else " "
        tags = "".join(f" #{g}" for g in t["tags"])
        print(f"{t['id']:>3} [{mark}] {t['text']}{tags}")


def cmd_search(words):
    # Chapter 8: search matches text and tags; closed tasks still searchable.
    # Fix (review): strip '#' per token so "#infra now" stays a two-word needle.
    needle = " ".join(w.lstrip("#") for w in words).lower()
    for t in load()["tasks"]:
        hay = (t["text"] + " " + " ".join(t["tags"])).lower()
        if needle in hay:
            mark = "x" if t["status"] == "done" else " "
            print(f"{t['id']:>3} [{mark}] {t['text']}")


def main(argv):
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(USAGE)
        return
    cmd = argv[0]
    if cmd == "version":
        print(f"tracker {VERSION}")
    elif cmd == "add":
        cmd_add(argv[1:])
    elif cmd == "close":
        try:
            cmd_close(int(argv[1]))
        except (IndexError, ValueError):
            sys.exit("close: usage — close <id>")
    elif cmd == "tag":
        try:
            cmd_tag(int(argv[1]), argv[2])
        except (IndexError, ValueError):
            sys.exit("tag: usage — tag <id> <tag>")
    elif cmd == "list":
        cmd_list()
    elif cmd == "search":
        cmd_search(argv[1:])
    else:
        sys.exit(USAGE)


if __name__ == "__main__":
    main(sys.argv[1:])
