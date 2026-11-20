import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "project-wiki/scripts/storage_inventory.py"
SPEC = importlib.util.spec_from_file_location("storage_inventory", SCRIPT)
assert SPEC and SPEC.loader
storage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(storage)


class StorageInventoryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()

    def write(self, path, n):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"x" * n)
        return target

    def test_groups_logical_bytes_and_does_not_claim_disk_savings(self):
        self.write("cache/a", 12)
        self.write("cache/nested/b", 15)
        self.write("docs.txt", 9)
        result = storage.inventory(self.root, 20, 4)
        self.assertEqual("complete_within_scan_policy", result["status"])
        self.assertEqual(36, result["apparent_bytes"])
        self.assertEqual([("cache", 27), ("docs.txt", 9)],
                         [(row["name"], row["apparent_bytes"])
                          for row in result["ranked_immediate_children"]])
        self.assertIsNone(result["allocated_bytes"])
        self.assertIsNone(result["reclaimable_bytes"])

    def test_excludes_external_or_protected_names_before_stat(self):
        self.write("private-name/child", 67)
        self.write("cache/nested/child", 31)
        self.write("cache/visible", 3)
        real_lstat = os.lstat

        def lstat(path, *args, **kwargs):
            self.assertNotIn(Path(path).name, ("private-name", "nested"))
            return real_lstat(path, *args, **kwargs)

        with patch.object(storage.os, "lstat", side_effect=lstat):
            result = storage.inventory(self.root, 20, 4, ["private-name", "cache/nested"])
        self.assertEqual(2, result["counts"]["excluded"])
        self.assertEqual(3, result["apparent_bytes"])
        self.assertNotIn("private-name", json.dumps(result))
        for bad in ("../a", "/a", "cache/../a", "cache//a", "cache/./b", "C:/x", "cache\\a"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                storage.inventory(self.root, 20, 4, [bad])

    def test_exclusion_is_unicode_normalized_and_case_insensitive(self):
        self.write("CAFÉ/protected", 31)
        self.write("cache/DÉPÔT/protected", 67)
        self.write("visible", 3)
        result = storage.inventory(self.root, 20, 4, ["cafe\u0301", "CACHE/de\u0301po\u0302t"])
        self.assertEqual(2, result["counts"]["excluded"])
        self.assertEqual(3, result["apparent_bytes"])
        self.assertNotIn("CAF", json.dumps(result))

    def test_visits_root_siblings_before_large_subtree(self):
        for i in range(10):
            self.write(f"a-big-cache/cache-{i}", i)
        self.write("b-sibling/retained", 50)
        self.write("c-top-file", 20)
        result = storage.inventory(self.root, 4, 4)
        self.assertTrue(result["root_entries_complete"])
        self.assertIn("entry_budget_reached", result["partial_reasons"])
        rows = {row["name"]: row for row in result["ranked_immediate_children"]}
        self.assertEqual({"a-big-cache", "b-sibling", "c-top-file"}, set(rows))
        self.assertEqual(20, rows["c-top-file"]["apparent_bytes"])
        self.assertTrue(rows["a-big-cache"]["partial"] or rows["b-sibling"]["partial"])
        self.assertFalse(storage.inventory(self.root, 2, 4)["root_entries_complete"])

    def test_bounds_entries_depth_and_visible_rows(self):
        self.write("cache/nested/payload", 72)
        result = storage.inventory(self.root, 20, 2)
        self.assertEqual(["depth_bound_reached"], result["partial_reasons"])
        self.assertTrue(result["ranked_immediate_children"][0]["partial"])
        self.assertEqual(0, result["apparent_bytes"])
        for i in range(29):
            self.write(f"file{i}", i)
        result = storage.inventory(self.root, 4, 4)
        self.assertEqual(4, result["counts"]["entries"])
        self.assertIn("entry_budget_reached", result["partial_reasons"])
        result = storage.inventory(self.root, 40, 4)
        self.assertEqual(len(result["ranked_immediate_children"]), 25)
        self.assertEqual(5, result["omitted_ranked_children"])
        self.assertEqual("cache", result["ranked_immediate_children"][0]["name"])

    def test_skips_real_symlink_and_rejects_symlink_in_root_path(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside).resolve()
            (target / "nested").mkdir()
            (target / "outside-file").write_bytes(b"external")
            link = self.root / "link"
            try:
                link.symlink_to(target, target_is_directory=True)
            except (NotImplementedError, OSError):
                self.skipTest("host does not allow directory symlinks")
            result = storage.inventory(self.root, 20, 4)
            self.assertEqual(0, result["apparent_bytes"])
            self.assertEqual(1, result["counts"]["links_or_reparse"])
            self.assertEqual([], result["ranked_immediate_children"])
            with self.assertRaisesRegex(ValueError, "links/reparse"):
                storage.inventory(link / "nested", 20, 4)

    def test_windows_reparse_and_foreign_device_flags_prevent_descent(self):
        self.write("junction/child", 37)
        self.write("fakemount/child", 40)
        real_lstat = os.lstat

        def lstat(path, *args, **kwargs):
            path = Path(path)
            self.assertNotEqual("child", path.name)
            info = real_lstat(path, *args, **kwargs)
            if path.name == "junction":
                return SimpleNamespace(st_mode=stat.S_IFDIR, st_dev=info.st_dev,
                                       st_file_attributes=storage.REPARSE_POINT)
            if path.name == "fakemount":
                return SimpleNamespace(st_mode=stat.S_IFDIR, st_dev=info.st_dev + 1)
            return info

        with patch.object(storage.os, "lstat", side_effect=lstat):
            result = storage.inventory(self.root, 20, 4)
        self.assertEqual(1, result["counts"]["links_or_reparse"])
        self.assertEqual(1, result["counts"]["foreign_filesystems"])
        self.assertEqual([], result["ranked_immediate_children"])

    def test_error_does_not_emit_secret_path(self):
        self.write("secret-name", 34)
        real_lstat = os.lstat

        def lstat(path, *args, **kwargs):
            if Path(path).name == "secret-name":
                raise PermissionError("Cannot inspect secret-name")
            return real_lstat(path, *args, **kwargs)

        with patch.object(storage.os, "lstat", side_effect=lstat):
            result = storage.inventory(self.root, 20, 4)
        self.assertEqual(1, result["counts"]["errors"])
        self.assertIn("unreadable_or_changed_entries", result["partial_reasons"])
        self.assertNotIn("secret-name", json.dumps(result))

    def test_cli_root_required_and_invalid_root_does_not_emit_name(self):
        for args in ([], ["--root", str(self.root / "secret-name")],
                     ["--root", str(self.root), "--max-entries", "100001"],
                     ["--root", str(self.root), "--exclude", "../secret-name"]):
            with self.subTest(args=args):
                result = subprocess.run([sys.executable, str(SCRIPT), *args],
                                        capture_output=True, text=True)
                self.assertEqual(2, result.returncode)
                self.assertFalse(result.stdout)
                self.assertNotIn("secret-name", result.stderr)
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root)],
                                capture_output=True, text=True, check=True)
        self.assertEqual(0, json.loads(result.stdout)["apparent_bytes"])


if __name__ == "__main__":
    unittest.main()
