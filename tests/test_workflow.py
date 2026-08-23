from __future__ import annotations

import os
import json
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
SESSION_HOOK = ROOT / "hooks" / "coherens_session_start.py"
PLUGIN_INSTALLER = ROOT / "tools" / "install_plugin.py"


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def complete_project_profile(knowledge_root: Path, project_id: str, commit: str) -> Path:
    profile = knowledge_root / "projects" / project_id / "PROJECT_PROFILE.md"
    content = profile.read_text(encoding="utf-8")
    content = content.replace("status: draft", f"verified_commit: {commit}\nstatus: active")
    replacements = {
        "## Purpose and scope\n\nNot recorded yet.":
            "## Purpose and scope\n\nA small document-processing project used for synchronization tests.",
        "## Architecture and execution flow\n\nNot recorded yet.":
            "## Architecture and execution flow\n\nA tracked input document is processed by the main project entry point.",
        "## Directory and module map\n\nNot recorded yet.":
            "## Directory and module map\n\n`README.md` documents the project and `app.py` is the executable module.",
        "## Key scripts and interfaces\n\nNot recorded yet.":
            "## Key scripts and interfaces\n\n`app.py` exposes the command-line entry point.",
        "## Setup, run, and verification\n\nNot recorded yet.":
            "## Setup, run, and verification\n\nRun `python app.py` and the workflow tests.",
        "## Dependencies and environments\n\nNot recorded yet.":
            "## Dependencies and environments\n\nPython 3.10 or newer on the registered test workspace.",
        "## Known constraints and open questions\n\nNot recorded yet.":
            "## Known constraints and open questions\n\nThe fixture intentionally covers a small project surface.",
        "## Evidence reviewed\n\nNot recorded yet.":
            "## Evidence reviewed\n\nReviewed `README.md`, `app.py`, Git state, and generated onboarding files.",
    }
    for old, new in replacements.items():
        content = content.replace(old, new)
    profile.write_text(content, encoding="utf-8")
    return profile


class WorkflowTest(unittest.TestCase):
    def test_readme_languages_and_cross_links(self) -> None:
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        self.assertTrue(english.isascii())
        self.assertIn('href="README.zh-CN.md">Chinese README</a>', english)
        self.assertIn('href="README.md">English README</a>', chinese)
        self.assertIn("配置 Coherens", chinese)

    def test_setup_skill_pins_canonical_repository(self) -> None:
        setup_skill = ROOT / "skills" / "coherens-setup" / "SKILL.md"
        content = setup_skill.read_text(encoding="utf-8")
        self.assertIn("https://github.com/ChengxiSHE/Coherens.git", content)
        self.assertIn("must never be public", content)

    def test_complete_plugin_installer_registers_personal_marketplace(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            target = temp_root / "plugins" / "coherens"
            marketplace = temp_root / ".agents" / "plugins" / "marketplace.json"
            result = run(
                str(PLUGIN_INSTALLER),
                "--target",
                str(target),
                "--marketplace",
                str(marketplace),
                "--no-enable",
            )
            self.assertIn('"enabled": false', result.stdout)
            self.assertTrue((target / ".codex-plugin" / "plugin.json").exists())
            self.assertTrue((target / "hooks" / "hooks.json").exists())
            data = json.loads(marketplace.read_text(encoding="utf-8"))
            self.assertEqual("personal", data["name"])
            self.assertEqual("coherens", data["plugins"][0]["name"])

    def test_setup_initializes_empty_private_vault(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            vault = temp_root / "private-vault"
            vault.mkdir()
            subprocess.run(["git", "init"], cwd=vault, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=vault, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=vault, check=True)
            remote = temp_root / "vault-remote.git"
            subprocess.run(["git", "init", "--bare", str(remote)], check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=vault, check=True)
            config = temp_root / "coherens-config.yaml"
            env = os.environ.copy()
            env["COHERENS_CONFIG"] = str(config)
            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_TOOL),
                    "setup",
                    "--vault-root",
                    str(vault),
                    "--machine-id",
                    "mac-dev-03",
                    "--vault-repository",
                    str(remote),
                    "--confirm-private",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                check=True,
            )
            self.assertIn('"initialized": true', result.stdout)
            self.assertTrue((vault / "registry.yaml").exists())
            self.assertTrue((vault / "PROJECT_MAP.md").exists())
            self.assertIn("machine_id: mac-dev-03", config.read_text(encoding="utf-8"))
            doctor = subprocess.run(
                [sys.executable, str(PROJECT_TOOL), "doctor", "--knowledge-root", str(vault)],
                cwd=temp_root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                check=True,
            )
            self.assertIn('"machine_ready": true', doctor.stdout)
            self.assertIn('"vault_ready": true', doctor.stdout)
            self.assertIn('"ready": true', doctor.stdout)

    def test_setup_requires_user_confirmed_private_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            vault = temp_root / "vault"
            vault.mkdir()
            subprocess.run(["git", "init"], cwd=vault, check=True, stdout=subprocess.DEVNULL)
            remote = temp_root / "vault-remote.git"
            subprocess.run(["git", "init", "--bare", str(remote)], check=True, stdout=subprocess.DEVNULL)
            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_TOOL),
                    "setup",
                    "--vault-root",
                    str(vault),
                    "--vault-repository",
                    str(remote),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(2, result.returncode)
            self.assertIn("--confirm-private", result.stderr)

    def test_session_hook_routes_missing_setup_without_reading_vault(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            env = os.environ.copy()
            env["COHERENS_CONFIG"] = str(temp_root / "missing-config.yaml")
            result = subprocess.run(
                [sys.executable, str(SESSION_HOOK)],
                cwd=temp_root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                check=True,
            )
            output = json.loads(result.stdout)
            context = output["hookSpecificOutput"]["additionalContext"]
            self.assertIn("not configured", context)

    def test_onboard_requires_project_origin(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            project_root = temp_root / "project"
            project_root.mkdir()
            subprocess.run(["git", "init"], cwd=project_root, check=True, stdout=subprocess.DEVNULL)
            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_TOOL),
                    "onboard",
                    "--project-root",
                    str(project_root),
                    "--knowledge-root",
                    str(ROOT),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(2, result.returncode)
            self.assertIn("origin remote", result.stderr)

    def test_initial_sync_requires_completed_project_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            knowledge_root = temp_root / "vault"
            shutil.copytree(ROOT, knowledge_root, ignore=shutil.ignore_patterns(".git", "generated"))
            project_root = temp_root / "project"
            project_root.mkdir()
            subprocess.run(["git", "init"], cwd=project_root, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=project_root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=project_root, check=True)
            (project_root / "app.py").write_text("print('hello')\n", encoding="utf-8")
            run(
                str(PROJECT_TOOL),
                "bootstrap",
                "--project-root",
                str(project_root),
                "--project-id",
                "project-a",
                "--workspace-id",
                "mac-dev-01",
                "--knowledge-root",
                str(knowledge_root),
                "--knowledge-repository",
                "example/vault",
                "--repository",
                "example/project-a",
            )
            subprocess.run(["git", "add", "."], cwd=project_root, check=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=project_root, check=True, stdout=subprocess.DEVNULL)
            profile = knowledge_root / "projects" / "project-a" / "PROJECT_PROFILE.md"
            profile.write_text(
                profile.read_text(encoding="utf-8").replace("status: active", "status: draft", 1),
                encoding="utf-8",
            )
            (project_root / ".kb" / "sync-state.json").write_text("{}\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_TOOL),
                    "sync",
                    "--project-root",
                    str(project_root),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(2, result.returncode)
            self.assertIn("active Project Profile", result.stderr)

    def test_validation_rejects_local_home_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            knowledge_root = Path(temp) / "vault"
            shutil.copytree(ROOT, knowledge_root, ignore=shutil.ignore_patterns(".git", "generated"))
            note = knowledge_root / "projects" / "project-a" / "common" / "local-path.md"
            note.write_text(
                "---\n"
                "type: collection\n"
                "id: project-a-local-path\n"
                "title: Local path leak\n"
                "project: project-a\n"
                "status: active\n"
                "---\n\n"
                "# Local path leak\n\nSource: `/Users/example/private/project`.\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(PROJECT_TOOL), "validate", "--knowledge-root", str(knowledge_root)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(2, result.returncode)
            self.assertIn("contains a local home-directory path", result.stdout)

    def test_agent_publish_infers_registers_validates_and_commits(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            knowledge_root = temp_root / "vault"
            shutil.copytree(
                ROOT,
                knowledge_root,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "generated"),
            )
            subprocess.run(["git", "init"], cwd=knowledge_root, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=knowledge_root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=knowledge_root, check=True)
            subprocess.run(["git", "add", "."], cwd=knowledge_root, check=True)
            subprocess.run(["git", "commit", "-m", "initialize vault"], cwd=knowledge_root, check=True, stdout=subprocess.DEVNULL)

            project_root = temp_root / "New Project"
            project_root.mkdir()
            subprocess.run(["git", "init"], cwd=project_root, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=project_root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=project_root, check=True)
            subprocess.run(
                ["git", "remote", "add", "origin", "git@github.com:example/new-project.git"],
                cwd=project_root,
                check=True,
            )
            (project_root / "README.md").write_text("# New Project\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=project_root, check=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=project_root, check=True, stdout=subprocess.DEVNULL)

            run(
                str(PROJECT_TOOL),
                "onboard",
                "--project-root",
                str(project_root),
                "--knowledge-root",
                str(knowledge_root),
                "--workspace-id",
                "mac-dev-02",
            )
            subprocess.run(
                ["git", "add", "README.md", "AGENTS.md", ".gitignore", ".kb/project.yaml"],
                cwd=project_root,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "connect project"],
                cwd=project_root,
                check=True,
                stdout=subprocess.DEVNULL,
            )
            commit = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=project_root,
                text=True,
                stdout=subprocess.PIPE,
                check=True,
            ).stdout.strip()
            complete_project_profile(knowledge_root, "new-project", commit)
            subprocess.run(["git", "add", "."], cwd=knowledge_root, check=True)
            subprocess.run(["git", "commit", "-m", "onboard project and profile"], cwd=knowledge_root, check=True, stdout=subprocess.DEVNULL)
            result = run(
                str(PROJECT_TOOL),
                "publish",
                "--project-root",
                str(project_root),
                "--knowledge-root",
                str(knowledge_root),
                "--workspace-id",
                "mac-dev-02",
                "--no-push",
            )
            self.assertIn('"project_id": "new-project"', result.stdout)
            self.assertIn('"committed": true', result.stdout)
            project_config = (project_root / ".kb" / "project.yaml").read_text(encoding="utf-8")
            self.assertIn("project_id: new-project", project_config)
            registry = (knowledge_root / "registry.yaml").read_text(encoding="utf-8")
            self.assertIn("new-project:", registry)
            self.assertTrue((knowledge_root / "projects" / "new-project" / "index.md").exists())
            self.assertIn(
                "status: active",
                (knowledge_root / "projects" / "new-project" / "PROJECT_PROFILE.md").read_text(
                    encoding="utf-8"
                ),
            )
            self.assertTrue((knowledge_root / "projects" / "new-project" / "workspaces" / "mac-dev-02.md").exists())
            self.assertEqual("", subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=knowledge_root,
                text=True,
                stdout=subprocess.PIPE,
                check=True,
            ).stdout)

            manifest = knowledge_root / "projects" / "new-project" / "manifest.yaml"
            manifest.write_text(
                manifest.read_text(encoding="utf-8").replace(
                    "  project-baseline: context-packs/project-baseline.md\n",
                    "  project-baseline: context-packs/project-baseline.md\n"
                    "  release: context-packs/release.md\n",
                ),
                encoding="utf-8",
            )
            subprocess.run(["git", "add", str(manifest)], cwd=knowledge_root, check=True)
            subprocess.run(["git", "commit", "-m", "add context pack route"], cwd=knowledge_root, check=True, stdout=subprocess.DEVNULL)
            run(
                str(PROJECT_TOOL),
                "publish",
                "--project-root",
                str(project_root),
                "--knowledge-root",
                str(knowledge_root),
                "--workspace-id",
                "mac-dev-02",
                "--no-push",
            )
            self.assertIn("release: context-packs/release.md", manifest.read_text(encoding="utf-8"))

    def test_template_validates_and_generates_graph(self) -> None:
        self.assertTrue((ROOT / "projects" / "project-a" / "logs" / "daily" / ".gitkeep").exists())
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
                "--repository",
                "example/project-a",
            )
            (project_root / "app.py").write_text("print('coherens fixture')\n", encoding="utf-8")
            subprocess.run(["git", "add", "app.py", "AGENTS.md", ".gitignore", ".kb/project.yaml"], cwd=project_root, check=True)
            subprocess.run(["git", "commit", "-m", "configure knowledge"], cwd=project_root, check=True, stdout=subprocess.DEVNULL)
            commit = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=project_root,
                text=True,
                stdout=subprocess.PIPE,
                check=True,
            ).stdout.strip()
            profile = knowledge_root / "projects" / "project-a" / "PROJECT_PROFILE.md"
            profile.write_text(
                profile.read_text(encoding="utf-8").replace(
                    "verified_commit: 8f4c21a", f"verified_commit: {commit}"
                ),
                encoding="utf-8",
            )

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
            (project_root / "app.py").write_text("print('changed but not committed')\n", encoding="utf-8")
            run(str(PROJECT_TOOL), "sync", "--project-root", str(project_root))
            logs = list((knowledge_root / "projects" / "project-a" / "logs").glob("*__mac-dev-01*.md"))
            self.assertEqual(2, len(logs))
            latest_workspace = knowledge_root / "projects" / "project-a" / "workspaces" / "mac-dev-01.md"
            workspace_content = latest_workspace.read_text(encoding="utf-8")
            self.assertIn("code_state: unanchored", workspace_content)
            self.assertNotIn("verified_commit:", workspace_content)
            self.assertNotIn(str(project_root), logs[-1].read_text(encoding="utf-8"))
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
