"""Contract for the shipped closeout route and its interrupted-work fixture."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "project-wiki"
FIXTURE = ROOT / "evals/fixture-project"


class MaintenanceCloseoutTests(unittest.TestCase):
    def test_closeout_and_new_project_template_are_reachable_from_skill(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        method = (SKILL / "references/maintenance.md").read_text(encoding="utf-8")
        self.assertIn("## Maintain project storage and close out development", skill)
        closeout = skill.split("## Maintain project storage and close out development", 1)[1].split("\n## ", 1)[0]
        self.assertIn("references/maintenance.md#closeout-and-maintenance-sweeps", closeout)
        self.assertIn("references/maintenance.md#maintenance-entry-template", closeout)
        self.assertIn("## Closeout and maintenance sweeps", method)
        self.assertIn("### Maintenance entry template", method)
        self.assertIn("## Maintenance", method)

    def test_fixture_entry_routes_to_interrupted_closeout(self):
        wiki = FIXTURE / "docs/wiki"
        entry = (wiki / "engineering-entry.md").read_text(encoding="utf-8")
        self.assertIn("## Maintenance", entry)
        maintenance = entry.split("## Maintenance", 1)[1].split("\n## ", 1)[0]
        self.assertRegex(maintenance, r"\]\(maintenance-closeout\.md#interrupted-retry-release\)")
        retained = (wiki / "maintenance-closeout.md").read_text(encoding="utf-8")
        names = set(re.findall(r"^## (.+)$", retained, flags=re.M))
        self.assertIn("Interrupted retry release", names)
        self.assertIn("Existing owner and receipt", names)
        self.assertIn("Resume decision", names)
        self.assertIn("[recovery owner](engineering-contracts.md#recovery)", retained)
        self.assertIn("live rollout not run", retained)
        self.assertIn("keep pending authority", retained)

    def test_native_wiki_query_finds_storage_inventory_without_running_it(self):
        for question in ("disk growth cleanup", "磁盘空间回收"):
            with self.subTest(question=question):
                result = subprocess.run(
                    [sys.executable, str(SKILL / "scripts/wiki.py"), "query",
                     "--root", str(FIXTURE), "--json", question],
                    check=True, text=True, encoding="utf-8", capture_output=True,
                    env={**os.environ, "PYTHONUTF8": "1"},
                )
                route = json.loads(result.stdout)["matches"][0]
                self.assertEqual(route["id"], "storage-maintenance")
                self.assertIn("docs/wiki/maintenance-closeout.md#storage-and-resource-inventory", route["docs"])
                self.assertEqual(route["evidence"]["implementation"], "planned")

    def test_storage_route_leads_to_packaged_inventory(self):
        # Walk the bundled example's authored route, not the expected-answer prose.
        page = FIXTURE / "docs/wiki/maintenance-closeout.md"
        link = re.search(r"\[read-only inventory procedure\]\(([^)]+)\)", page.read_text(encoding="utf-8"))
        self.assertIsNotNone(link)
        path, anchor = link.group(1).split("#", 1)
        method = (page.parent / path).resolve()
        self.assertEqual(anchor, "inventory-storage-without-cleaning-it")
        self.assertEqual(method, SKILL / "references/maintenance.md")
        section = method.read_text(encoding="utf-8").split("### Inventory storage without cleaning it", 1)[1].split("\n### ", 1)[0]
        cli = re.search(r"python <skill>/([^ ]+) --root", section)
        self.assertIsNotNone(cli)
        with tempfile.TemporaryDirectory() as work:
            # On macOS /tmp can be a symlink; the scanner requires real roots.
            root = Path(work).resolve()
            (root / "build").mkdir()
            (root / "build/candidate").write_bytes(b"x" * 128)
            (root / "protected").mkdir()
            (root / "protected/private").write_bytes(b"not inventoried")
            result = subprocess.run(
                [sys.executable, str(SKILL / cli.group(1)), "--root", str(root),
                 "--exclude", "protected"],
                check=True, text=True, encoding="utf-8", capture_output=True,
            )
            report = json.loads(result.stdout)
            self.assertEqual(report["apparent_bytes"], 128)
            self.assertEqual(report["counts"]["excluded"], 1)
            self.assertEqual(report["ranked_immediate_children"][0]["name"], "build")
            self.assertNotIn("protected", result.stdout)
            self.assertIsNone(report["reclaimable_bytes"])
            self.assertEqual((root / "protected/private").read_bytes(), b"not inventoried")
