from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_TOOL = ROOT / "skills" / "project-knowledge" / "scripts" / "project_knowledge.py"
GRAPH_TOOL = ROOT / "skills" / "knowledge-graph-view" / "scripts" / "knowledge_graph.py"


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


class WorkflowTest(unittest.TestCase):
    def test_template_validates_and_generates_graph(self) -> None:
        result = run(str(PROJECT_TOOL), "validate", "--knowledge-root", str(ROOT))
        self.assertIn("Validated", result.stdout)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "graph.html"
            result = run(
                str(GRAPH_TOOL),
                "--knowledge-root",
                str(ROOT),
                "--output",
                str(output),
            )
            self.assertIn("nodes and", result.stdout)
            content = output.read_text(encoding="utf-8")
            self.assertIn("project-a", content)
            self.assertIn("Docker training", content)
            node = shutil.which("node")
            if node:
                script_match = re.search(r"<script>\n(.*)\n</script>", content, re.DOTALL)
                self.assertIsNotNone(script_match)
                script_path = Path(temp) / "graph.js"
                script_path.write_text(script_match.group(1), encoding="utf-8")
                subprocess.run([node, "--check", str(script_path)], check=True)

    def test_bootstrap_incremental_sync_and_daily_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            knowledge_root = temp_root / "knowledge"
            shutil.copytree(ROOT, knowledge_root)
            project_root = temp_root / "code"
            project_root.mkdir()
            subprocess.run(["git", "init"], cwd=project_root, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=project_root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=project_root, check=True)

            run(
                str(PROJECT_TOOL),
                "bootstrap",
                "--project-root",
                str(project_root),
                "--project-id",
                "project-a",
                "--workspace-id",
                "mac-dev-01",
                "--version-track",
                "main",
                "--knowledge-root",
                str(knowledge_root),
                "--knowledge-repository",
                "example/engineering-knowledge",
            )
            subprocess.run(["git", "add", "AGENTS.md", ".gitignore", ".kb/project.yaml"], cwd=project_root, check=True)
            subprocess.run(["git", "commit", "-m", "configure knowledge"], cwd=project_root, check=True, stdout=subprocess.DEVNULL)

            run(str(PROJECT_TOOL), "sync", "--project-root", str(project_root))
            progress = project_root / "PROGRESS.md"
            progress.write_text(
                progress.read_text(encoding="utf-8")
                + "\n## 2026-08-23 18:00 | mac-dev-01\n\n"
                + "- Changed: Added checkpoint recovery.\n"
                + "- Verified: Small training run passed.\n"
                + "- Promote to shared knowledge: yes\n",
                encoding="utf-8",
            )
            run(str(PROJECT_TOOL), "sync", "--project-root", str(project_root))
            logs = list((knowledge_root / "projects" / "project-a" / "logs").glob("*__mac-dev-01*.md"))
            self.assertEqual(2, len(logs))
            date = logs[0].name[:10]
            run(
                str(PROJECT_TOOL),
                "daily-summary",
                "--knowledge-root",
                str(knowledge_root),
                "--date",
                date,
            )
            daily = knowledge_root / "projects" / "project-a" / "logs" / "daily" / f"{date}.md"
            self.assertTrue(daily.exists())
            self.assertIn("Promotion candidates", daily.read_text(encoding="utf-8"))
            run(str(PROJECT_TOOL), "validate", "--knowledge-root", str(knowledge_root))


if __name__ == "__main__":
    unittest.main()
