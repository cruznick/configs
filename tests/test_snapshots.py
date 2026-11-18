"""Isolated snapshot integrity, deduplication and scope checks."""

import contextlib
import io
from pathlib import Path
import runpy
import sqlite3
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "bin/executable_dots-snapshot"
MODULE = runpy.run_path(str(SCRIPT))
CREATE = MODULE["create"]
VERIFY = MODULE["verify"]
GLOBALS = CREATE.__globals__


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "home"
        self.home.mkdir()
        (self.home / ".zshrc").write_text("original\n")

    def capture(self, name, items=None):
        root = self.home / "Backups" / name
        with patch.dict(GLOBALS, {
            "HOME_ITEMS": items or [".zshrc"],
            "APP_SUPPORT": [], "PREFERENCE_DOMAINS": [],
        }), patch.object(GLOBALS["sys"], "platform", "darwin"), patch.object(
            GLOBALS["subprocess"], "run",
            return_value=subprocess.CompletedProcess([], 0, b"fixture\n", b""),
        ), contextlib.redirect_stdout(io.StringIO()):
            CREATE(root, self.home)
        return root

    def test_unchanged_files_share_storage_but_sources_and_changes_do_not(self):
        one = self.capture("current-state-01")
        two = self.capture("current-state-02")
        first = one / "home/.zshrc"
        second = two / "home/.zshrc"
        self.assertEqual(first.stat().st_ino, second.stat().st_ino)
        self.assertNotEqual(first.stat().st_ino, (self.home / ".zshrc").stat().st_ino)
        (self.home / ".zshrc").write_text("changed\n")
        three = self.capture("current-state-03")
        self.assertEqual(first.read_text(), "original\n")
        self.assertNotEqual(first.stat().st_ino, (three / "home/.zshrc").stat().st_ino)

    def test_verification_rejects_tampering_and_extra_files(self):
        root = self.capture("current-state-01")
        (root / "home/.zshrc").write_text("tampered\n")
        with self.assertRaisesRegex(RuntimeError, "Checksum"):
            VERIFY(root)
        (root / "extra").touch()
        with self.assertRaisesRegex(RuntimeError, "file set"):
            VERIFY(root)

    def test_sqlite_wal_and_symlink_are_captured_without_following(self):
        database = self.home / "settings.db"
        with sqlite3.connect(database) as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("CREATE TABLE settings (value TEXT)")
            connection.execute("INSERT INTO settings VALUES ('committed')")
            connection.commit()
            (self.home / "selector").symlink_to("/nonexistent/external-key")
            root = self.capture("current-state-01", ["settings.db", "selector"])
            with sqlite3.connect(root / "home/settings.db") as recovered:
                self.assertEqual(recovered.execute("SELECT value FROM settings").fetchone(), ("committed",))
        self.assertEqual((root / "home/selector").readlink(), Path("/nonexistent/external-key"))

    def test_default_scope_excludes_repository_and_session_trees(self):
        items = GLOBALS["HOME_ITEMS"]
        self.assertNotIn("repos", items)
        self.assertNotIn(".codex", items)
        self.assertNotIn(".claude", items)
        self.assertFalse(any("sessions" in item for item in items))
        root = self.capture("current-state-01")
        with self.assertRaisesRegex(RuntimeError, "already exists"):
            CREATE(root, self.home)


if __name__ == "__main__":
    unittest.main()
