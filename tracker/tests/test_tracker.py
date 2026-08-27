"""Tracker's test suite — grown chapter by chapter (Ch2 atomicity, Ch5 determinism, Ch8 features)."""
import importlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tracker as tr


class TrackerTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data_file = Path(self.tmp.name) / "tasks.json"
        patcher = mock.patch.object(tr, "DATA", self.data_file)
        patcher.start()
        self.addCleanup(patcher.stop)

    # Chapter 1-2: the core contract ------------------------------------

    def test_add_assigns_incrementing_ids(self):
        tr.cmd_add(["first task"])
        tr.cmd_add(["second"])
        ids = [t["id"] for t in tr.load()["tasks"]]
        self.assertEqual(ids, [1, 2])

    def test_multiline_and_quoted_text_survives(self):
        # Chapter 2's original bug: shell-fragmented quotes.
        tr.cmd_add(['fix', 'the', '"login"', 'bug'])
        self.assertEqual(tr.load()["tasks"][0]["text"], 'fix the "login" bug')

    def test_close_marks_done(self):
        tr.cmd_add(["task"])
        tr.cmd_close(1)
        self.assertEqual(tr.load()["tasks"][0]["status"], "done")

    # Chapter 2: atomic writes -------------------------------------------

    def test_failed_save_never_truncates_real_data(self):
        tr.cmd_add(["survive"])
        real = self.data_file.read_text()
        with mock.patch.object(json, "dump", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                tr.cmd_add(["doomed"])
        self.assertEqual(self.data_file.read_text(), real)      # intact
        data = tr.load()
        self.assertEqual(len(data["tasks"]), 1)                 # only the survivor

    def test_corrupt_file_is_backed_up_not_destroyed(self):
        tr.cmd_add(["precious"])
        self.data_file.write_text("{not json at all")
        data = tr.load()
        self.assertEqual(data["tasks"], [])                      # clean start
        backup = self.data_file.with_name("tasks.corrupt.json")
        self.assertIn("not json", backup.read_text())            # evidence kept

    def test_second_corruption_never_overwrites_the_first_backup(self):
        tr.cmd_add(["first incident"])
        self.data_file.write_text("{bad one")
        tr.load()                                               # -> tasks.corrupt.json
        self.data_file.write_text("{bad two")
        tr.load()                                               # -> tasks.corrupt-1.json
        self.assertTrue((self.data_file.with_name("tasks.corrupt-1.json")).exists())

    def test_search_handles_hashed_multiword_needles(self):
        # Fix (review): '#' is stripped per token, so ["#infra", "now"] searches
        # "infra now" — and a mid-phrase hash token keeps the needle well-formed.
        tr.cmd_add(["audit infra now", "#sec"])
        out = []
        with mock.patch("builtins.print", out.append):
            tr.cmd_search(["#infra", "now"])
        self.assertEqual(len(out), 1)
        out2 = []
        with mock.patch("builtins.print", out2.append):
            tr.cmd_search(["audit", "#infra"])
        self.assertEqual(len(out2), 1)   # mid-phrase hash: needle "audit infra"

    def test_close_with_bad_args_exits_gracefully(self):
        tr.cmd_add(["task"])
        with self.assertRaises(SystemExit):
            tr.main(["close", "abc"])

    # Chapter 8: tags + search --------------------------------------------

    def test_hash_tokens_become_tags(self):
        tr.cmd_add(["rotate", "keys", "#infra", "#security"])
        t = tr.load()["tasks"][0]
        self.assertEqual(t["text"], "rotate keys")
        self.assertEqual(t["tags"], ["infra", "security"])

    def test_tag_command_adds_tag(self):
        tr.cmd_add(["task"])
        tr.cmd_tag(1, "#later")
        self.assertEqual(tr.load()["tasks"][0]["tags"], ["later"])

    def test_search_matches_text_and_tags(self):
        tr.cmd_add(["rotate", "keys", "#infra"])
        tr.cmd_add(["write", "the", "docs"])
        out = []
        with mock.patch("builtins.print", out.append):
            tr.cmd_search(["#infra"])
        self.assertEqual(len(out), 1)
        self.assertIn("rotate", out[0])

    def test_closed_tasks_still_searchable(self):
        tr.cmd_add(["old", "bug"])
        tr.cmd_close(1)
        out = []
        with mock.patch("builtins.print", out.append):
            tr.cmd_search(["bug"])
        self.assertEqual(len(out), 1)

    # Chapter 5: determinism (the Tuesday fix) -----------------------------

    def test_listing_is_deterministic_regardless_of_order(self):
        # Fix (review): exercise the PRINTED output, not load()'s order.
        for i in range(20):
            tr.cmd_add([f"task-{i}"])
        out = []
        with mock.patch("builtins.print", out.append):
            tr.cmd_list()
        ids = [int(line.split()[0]) for line in out]
        self.assertEqual(ids, sorted(ids))                       # id order, always


if __name__ == "__main__":
    unittest.main()
