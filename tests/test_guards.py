#!/usr/bin/env python3
"""Comprehensive test suite for destructive-cmd-guard and mpm-git-guard scripts."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GUARD_SCRIPT = os.path.join(REPO_DIR, "scripts", "destructive-cmd-guard.py")
GIT_GUARD_SCRIPT = os.path.join(REPO_DIR, "scripts", "mpm-git-guard.py")
LIVE_WATCH_SCRIPT = os.path.join(REPO_DIR, "scripts", "mpm-live-watch.py")


class TestDestructiveCmdGuard(unittest.TestCase):
    """Test suite for destructive-cmd-guard.py PreToolUse hook script."""

    def run_guard(self, cmd_line: str, artifact_dir: str = "", transcript_path: str = "", cwd: str = "") -> dict:
        payload = {
            "hookEventName": "PreToolUse",
            "cwd": cwd or "/tmp",
            "artifactDirectoryPath": artifact_dir,
            "transcriptPath": transcript_path,
            "toolCall": {
                "name": "run_command",
                "args": {
                    "CommandLine": cmd_line
                }
            }
        }
        proc = subprocess.run(
            [sys.executable, GUARD_SCRIPT, "--lang", "en"],
            input=json.dumps(payload),
            text=True,
            capture_output=True
        )
        self.assertEqual(proc.returncode, 0, f"Guard script exited with non-zero code: {proc.stderr}")
        return json.loads(proc.stdout)

    def test_chained_commands_git_clean_deny(self):
        res = self.run_guard('rm -f a && git -C "/tmp/Repo With Spaces" clean -fd')
        self.assertEqual(res.get("decision"), "deny")

    def test_git_reset_hard_deny(self):
        res = self.run_guard("git reset --hard HEAD~1")
        self.assertEqual(res.get("decision"), "deny")

    def test_git_checkout_dashdash_deny(self):
        res = self.run_guard("git checkout -- src/a.py")
        self.assertEqual(res.get("decision"), "deny")

    def test_git_checkout_dot_deny(self):
        res = self.run_guard("git checkout .")
        self.assertEqual(res.get("decision"), "deny")

    def test_git_checkout_branch_allow(self):
        res = self.run_guard("git checkout -b teamwork/fix")
        self.assertEqual(res.get("decision"), "allow")

    def test_git_restore_staged_allow(self):
        res = self.run_guard("git restore --staged foo.py")
        self.assertEqual(res.get("decision"), "allow")

    def test_git_restore_worktree_deny(self):
        res = self.run_guard("git restore foo.py")
        self.assertEqual(res.get("decision"), "deny")

    def test_rm_catastrophic_dot_deny(self):
        res = self.run_guard("rm -rf .")
        self.assertEqual(res.get("decision"), "deny")

    def test_rm_repo_file_force_ask(self):
        res = self.run_guard("rm -f foo.py", cwd="/opt/my-repo")
        self.assertEqual(res.get("decision"), "force_ask")

    def test_rm_scratch_file_allow(self):
        with tempfile.TemporaryDirectory() as tmp_art:
            scratch_dir = os.path.join(tmp_art, "scratch")
            os.makedirs(scratch_dir, exist_ok=True)
            scratch_file = os.path.join(scratch_dir, "tmp.py")
            res = self.run_guard(f"rm -f {scratch_file}", artifact_dir=tmp_art)
            self.assertEqual(res.get("decision"), "allow")

    def test_rm_parent_and_appdata_scratch_allow(self):
        app_dir = "/opt/fake-agy-app"
        child_art = os.path.join(app_dir, "brain", "child-uuid")
        parent_scratch = os.path.join(app_dir, "brain", "parent-uuid", "scratch")
        global_scratch = os.path.join(app_dir, "scratch", "teamwork")
        parent_transcript = os.path.join(app_dir, "brain", "parent-uuid", ".system_generated", "logs", "transcript.jsonl")

        res_parent = self.run_guard(f"rm -f {os.path.join(parent_scratch, 'tmp.py')}", artifact_dir=child_art)
        self.assertEqual(res_parent.get("decision"), "allow")

        res_global = self.run_guard(f"rm -f {os.path.join(global_scratch, 'note.md')}", artifact_dir=child_art)
        self.assertEqual(res_global.get("decision"), "allow")

        res_logs = self.run_guard(f"rm -f {parent_transcript}", artifact_dir=child_art)
        self.assertEqual(res_logs.get("decision"), "force_ask")

    def test_rm_tmp_file_allow(self):
        res = self.run_guard("rm -f /tmp/test.txt")
        self.assertEqual(res.get("decision"), "allow")

    def test_grep_quoted_pattern_allow(self):
        res = self.run_guard('grep -n "git clean" README.md')
        self.assertEqual(res.get("decision"), "allow")

    def test_git_commit_quoted_msg_allow(self):
        res = self.run_guard('git commit -m "ban git clean"')
        self.assertEqual(res.get("decision"), "allow")

    def test_python_inline_deletion_force_ask(self):
        res = self.run_guard('python3 -c "import os; os.remove(\'src/a.py\')"')
        self.assertEqual(res.get("decision"), "force_ask")


class TestMpmGitGuard(unittest.TestCase):
    """Test suite for mpm-git-guard.py CLI subcommands."""

    def run_git(self, repo: str, *args: str) -> None:
        cmd = ["git", "-C", repo] + list(args)
        subprocess.run(cmd, check=True, capture_output=True)

    def test_zero_commit_repo_snapshot(self):
        with tempfile.TemporaryDirectory() as base_tmp:
            repo_dir = os.path.join(base_tmp, "zero_repo")
            scratch_dir = os.path.join(base_tmp, "scratch")
            os.makedirs(repo_dir)
            self.run_git(repo_dir, "init")

            # Create an untracked file
            with open(os.path.join(repo_dir, "README.md"), "w") as f:
                f.write("# Hello\n")

            proc = subprocess.run(
                [sys.executable, GIT_GUARD_SCRIPT, "snapshot", "--repo", repo_dir, "--out", scratch_dir],
                capture_output=True,
                text=True
            )
            self.assertEqual(proc.returncode, 0, f"Snapshot failed: {proc.stderr}")
            self.assertTrue(os.path.isfile(os.path.join(scratch_dir, "baseline-meta.json")))
            self.assertTrue(os.path.isfile(os.path.join(scratch_dir, "baseline-untracked.txt")))

    def test_lifecycle_snapshot_audit_restore(self):
        with tempfile.TemporaryDirectory() as base_tmp:
            repo_dir = os.path.join(base_tmp, "repo with spaces")
            scratch_dir = os.path.join(base_tmp, "scratch")
            os.makedirs(repo_dir)

            self.run_git(repo_dir, "init")
            self.run_git(repo_dir, "config", "user.name", "Test Runner")
            self.run_git(repo_dir, "config", "user.email", "runner@example.com")

            # 1. Tracked file
            tracked_file = os.path.join(repo_dir, "tracked.txt")
            with open(tracked_file, "w") as f:
                f.write("Initial tracked content\n")
            self.run_git(repo_dir, "add", "tracked.txt")
            self.run_git(repo_dir, "commit", "-m", "Initial commit")

            # 2. Modify tracked file (uncommitted dirty state)
            with open(tracked_file, "w") as f:
                f.write("Modified tracked content\n")

            # 3. Untracked file in subfolder with spaces
            sub_dir = os.path.join(repo_dir, "sub folder")
            os.makedirs(sub_dir)
            untracked_file = os.path.join(sub_dir, "untracked file.txt")
            with open(untracked_file, "w") as f:
                f.write("Important untracked user WIP\n")

            # 4. Take snapshot
            snap_res = subprocess.run(
                [sys.executable, GIT_GUARD_SCRIPT, "snapshot", "--repo", repo_dir, "--out", scratch_dir],
                capture_output=True,
                text=True
            )
            self.assertEqual(snap_res.returncode, 0, f"Snapshot failed: {snap_res.stderr}")

            # 5. Audit should initially pass
            audit_pass = subprocess.run(
                [sys.executable, GIT_GUARD_SCRIPT, "audit", "--repo", repo_dir, "--baseline", scratch_dir],
                capture_output=True,
                text=True
            )
            self.assertEqual(audit_pass.returncode, 0, f"Audit unexpectedly failed: {audit_pass.stdout}")

            # 6. Delete both tracked and untracked files
            os.remove(untracked_file)
            self.run_git(repo_dir, "checkout", "HEAD", "--", "tracked.txt")
            # Or remove tracked file completely
            os.remove(tracked_file)

            # 7. Audit should FAIL (exit 2)
            audit_fail = subprocess.run(
                [sys.executable, GIT_GUARD_SCRIPT, "audit", "--repo", repo_dir, "--baseline", scratch_dir],
                capture_output=True,
                text=True
            )
            self.assertEqual(audit_fail.returncode, 2)
            report = json.loads(audit_fail.stdout)
            self.assertEqual(report.get("status"), "FAIL")
            self.assertIn("tracked.txt", report.get("deleted_tracked"))
            self.assertIn("sub folder/untracked file.txt", report.get("missing_untracked"))

            # 8. Restore files using restore --only-missing
            restore_res = subprocess.run(
                [sys.executable, GIT_GUARD_SCRIPT, "restore", "--repo", repo_dir, "--baseline", scratch_dir],
                capture_output=True,
                text=True
            )
            self.assertEqual(restore_res.returncode, 0, f"Restore failed: {restore_res.stderr}")

            # 9. Verify files are back on disk with expected content
            self.assertTrue(os.path.exists(untracked_file))
            self.assertTrue(os.path.exists(tracked_file))
            with open(untracked_file, "r") as f:
                self.assertEqual(f.read(), "Important untracked user WIP\n")
            with open(tracked_file, "r") as f:
                self.assertEqual(f.read(), "Modified tracked content\n")

            # 10. Audit should now PASS (exit 0)
            audit_pass2 = subprocess.run(
                [sys.executable, GIT_GUARD_SCRIPT, "audit", "--repo", repo_dir, "--baseline", scratch_dir],
                capture_output=True,
                text=True
            )
            self.assertEqual(audit_pass2.returncode, 0, f"Audit failed after restore: {audit_pass2.stdout}")

    def test_secret_scan(self):
        with tempfile.TemporaryDirectory() as base_tmp:
            clean_file = os.path.join(base_tmp, "clean.py")
            with open(clean_file, "w") as f:
                f.write("API_URL = 'https://api.example.com/v1'\n")

            proc_clean = subprocess.run(
                [sys.executable, GIT_GUARD_SCRIPT, "secret-scan", "--repo", base_tmp, "--files", clean_file],
                capture_output=True,
                text=True
            )
            self.assertEqual(proc_clean.returncode, 0)

            secret_file = os.path.join(base_tmp, "secret.env")
            with open(secret_file, "w") as f:
                # Synthetic dummy secret pattern (split to avoid tripping repo secret scanners)
                f.write("AWS_KEY = " + "AKIA" + "IOSFODNN7EXAMPLE\n")

            proc_secret = subprocess.run(
                [sys.executable, GIT_GUARD_SCRIPT, "secret-scan", "--repo", base_tmp, "--files", secret_file],
                capture_output=True,
                text=True
            )
            self.assertEqual(proc_secret.returncode, 1)
            self.assertIn("AWS Access Key ID", proc_secret.stdout)


class TestMpmLiveWatch(unittest.TestCase):
    """Test suite for mpm-live-watch.py zero-token OS continuous monitor."""

    def test_clean_max_runtime_exit_zero(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            transcript = os.path.join(tmp_dir, "transcript.jsonl")
            with open(transcript, "w") as f:
                f.write(json.dumps({"content": "Hello"}) + "\n")

            proc = subprocess.run(
                [
                    sys.executable,
                    LIVE_WATCH_SCRIPT,
                    "--transcript",
                    transcript,
                    "--interval",
                    "0.1",
                    "--max-runtime",
                    "0.25",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0)

    def test_deletion_detected_exit_ten(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_dir = os.path.join(tmp_dir, "repo")
            scratch_dir = os.path.join(tmp_dir, "scratch")
            os.makedirs(repo_dir)
            os.makedirs(scratch_dir)

            subprocess.run(["git", "-C", repo_dir, "init"], check=True, capture_output=True)
            baseline_txt = os.path.join(scratch_dir, "baseline-untracked.txt")
            with open(baseline_txt, "w") as f:
                f.write("user_wip.txt\n")

            # Missing from disk
            proc = subprocess.run(
                [
                    sys.executable,
                    LIVE_WATCH_SCRIPT,
                    "--repo",
                    repo_dir,
                    "--baseline",
                    scratch_dir,
                    "--interval",
                    "0.1",
                    "--max-runtime",
                    "1.0",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 10)
            data = json.loads(proc.stdout)
            self.assertEqual(data.get("alert"), "DELETION_DETECTED")

    def test_dangerous_command_exit_eleven(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            transcript = os.path.join(tmp_dir, "transcript.jsonl")
            step = {
                "tool_calls": [
                    {
                        "name": "run_command",
                        "args": {"CommandLine": "git clean -fd"},
                    }
                ]
            }
            with open(transcript, "w") as f:
                f.write(json.dumps(step) + "\n")

            proc = subprocess.run(
                [
                    sys.executable,
                    LIVE_WATCH_SCRIPT,
                    "--transcript",
                    transcript,
                    "--interval",
                    "0.1",
                    "--max-runtime",
                    "1.0",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 11)
            data = json.loads(proc.stdout)
            self.assertEqual(data.get("alert"), "DANGEROUS_COMMAND")

    def test_error_loop_exit_twelve(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            transcript = os.path.join(tmp_dir, "transcript.jsonl")
            with open(transcript, "w") as f:
                f.write(json.dumps({"status": "ERROR", "content": "Failed step 1"}) + "\n")
                f.write(json.dumps({"status": "ERROR", "content": "Failed step 2"}) + "\n")

            proc = subprocess.run(
                [
                    sys.executable,
                    LIVE_WATCH_SCRIPT,
                    "--transcript",
                    transcript,
                    "--interval",
                    "0.1",
                    "--max-errors",
                    "2",
                    "--max-runtime",
                    "1.0",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 12)
            data = json.loads(proc.stdout)
            self.assertEqual(data.get("alert"), "ERROR_LOOP")

    def test_read_only_tilt_exit_thirteen(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            transcript = os.path.join(tmp_dir, "transcript.jsonl")
            with open(transcript, "w") as f:
                for i in range(4):
                    step = {
                        "tool_calls": [{"name": "read_file", "args": {"Path": f"file_{i}.py"}}]
                    }
                    f.write(json.dumps(step) + "\n")

            proc = subprocess.run(
                [
                    sys.executable,
                    LIVE_WATCH_SCRIPT,
                    "--transcript",
                    transcript,
                    "--interval",
                    "0.1",
                    "--read-tilt",
                    "3",
                    "--max-runtime",
                    "1.0",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 13)
            data = json.loads(proc.stdout)
            self.assertEqual(data.get("alert"), "READ_ONLY_TILT")

    def test_completed_transcript_no_false_coma(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            transcript = os.path.join(tmp_dir, "transcript.jsonl")
            with open(transcript, "w") as f:
                f.write(json.dumps({"type": "PLANNER_RESPONSE", "status": "DONE", "tool_calls": []}) + "\n")

            proc = subprocess.run(
                [
                    sys.executable,
                    LIVE_WATCH_SCRIPT,
                    "--transcript",
                    transcript,
                    "--interval",
                    "0.05",
                    "--stale-sec",
                    "0.15",
                    "--max-runtime",
                    "0.35",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, f"Unexpected alert on completed transcript: {proc.stdout}")


if __name__ == "__main__":
    unittest.main()
