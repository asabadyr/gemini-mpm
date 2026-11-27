#!/usr/bin/env python3
"""Comprehensive test suite for destructive-cmd-guard and mpm-git-guard scripts."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GUARD_SCRIPT = os.path.join(REPO_DIR, "scripts", "destructive-cmd-guard.py")
GIT_GUARD_SCRIPT = os.path.join(REPO_DIR, "scripts", "mpm-git-guard.py")
LIVE_WATCH_SCRIPT = os.path.join(REPO_DIR, "scripts", "mpm-live-watch.py")
MPM_PY_SCRIPT = os.path.join(REPO_DIR, "scripts", "mpm-py")
RU_MPM_PY_SCRIPT = os.path.join(REPO_DIR, "ru", "scripts", "mpm-py")
INSTALL_SCRIPT = os.path.join(REPO_DIR, "install.sh")


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

    def test_shell_comment_with_apostrophe_allow(self):
        cmd = (
            "set -e\n"
            "# Note: when auth is enabled, let's probe health and AI endpoints\n"
            "kubectl -n smc port-forward svc/gateway 18086:8080 >/tmp/pf.log 2>&1 &\n"
            "curl -fsS http://127.0.0.1:18086/healthz\n"
        )
        res = self.run_guard(cmd)
        self.assertEqual(res.get("decision"), "allow")

    def test_shell_comment_still_blocks_following_destructive_cmd(self):
        cmd = "# Note: let's inspect first\ngit clean -fd\n"
        res = self.run_guard(cmd)
        self.assertEqual(res.get("decision"), "deny")

    def test_backslash_line_continuation_before_and_allow(self):
        cmd = (
            'git add \\\n'
            '  src/a.py \\\n'
            '  && git commit -m "ok" \\\n'
            '  && git status -s'
        )
        res = self.run_guard(cmd)
        self.assertEqual(res.get("decision"), "allow")

    def test_bash_array_assignment_and_commit_allow(self):
        cmd = (
            'FILES=(\n'
            '  crates/gw/src/main.rs\n'
            '  web/src/App.tsx\n'
            ')\n'
            'git add "${FILES[@]}" \\\n'
            '&& git commit -m "feat: safe commit" \\\n'
            '&& git status -s'
        )
        res = self.run_guard(cmd)
        self.assertEqual(res.get("decision"), "allow")

    def test_heredoc_file_write_with_apostrophes_and_semicolons_allow(self):
        cmd = (
            "cat << 'EOF' > /tmp/check_cyrillic.py\n"
            "import re\n"
            "# don't match comments; keep 'quotes' clean\n"
            "msg = \"it's fine; really\"\n"
            "print(msg)\n"
            "EOF\n"
            "python3 /tmp/check_cyrillic.py"
        )
        res = self.run_guard(cmd)
        self.assertEqual(res.get("decision"), "allow")

    def test_heredoc_python_safe_vs_destructive(self):
        safe_cmd = (
            "python3 - << 'PY'\n"
            "txt = \"don't fail; parse cleanly\"\n"
            "print(txt)\n"
            "PY"
        )
        self.assertEqual(self.run_guard(safe_cmd).get("decision"), "allow")

        chained_bad = (
            "python3 - << 'PY' && echo done\n"
            "import os\n"
            "os.remove('src/important.py')\n"
            "PY"
        )
        self.assertEqual(self.run_guard(chained_bad).get("decision"), "force_ask")

    def test_arithmetic_bitshift_not_mistaken_for_heredoc(self):
        cmd = "echo $((1 << 2)) && git clean -fd"
        res = self.run_guard(cmd)
        self.assertEqual(res.get("decision"), "deny")

    def test_unparseable_fallback_allows_benign_flags_destructive(self):
        self.assertEqual(self.run_guard('curl -sS "http://127.0.0.1:8080/health?x=unbalanced\'quote').get("decision"), "allow")
        self.assertEqual(self.run_guard('rm -rf "unbalanced_quote', cwd="/opt/repo").get("decision"), "force_ask")
        self.assertEqual(self.run_guard('git reset --hard "unbalanced_quote').get("decision"), "force_ask")

    def test_tmp_glob_prefix_allow_vs_broad_tmp_wildcard_force_ask(self):
        self.assertEqual(self.run_guard("rm -f /tmp/app_probe_*.log").get("decision"), "allow")
        self.assertEqual(self.run_guard("rm -rf /tmp/*").get("decision"), "force_ask")
        self.assertEqual(self.run_guard("rm -rf $TMPDIR/*").get("decision"), "force_ask")
        self.assertEqual(self.run_guard("rm -f src/*.py", cwd="/opt/repo").get("decision"), "force_ask")


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



class TestMpmPyWrapper(unittest.TestCase):
    """Test suite for scripts/mpm-py runtime wrapper."""

    def test_env_override_python(self):
        """(a) Test AGY_MPM_PYTHON override."""
        env = dict(os.environ)
        env["AGY_MPM_PYTHON"] = sys.executable
        proc = subprocess.run(
            [MPM_PY_SCRIPT, "--print-python"],
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr}")
        self.assertEqual(proc.stdout.strip(), sys.executable)

    def test_pin_file_resolution_with_fake_path_stub(self):
        """(b) Test agy-mpm-core.env pin resolution even when PATH contains fake < 3.8 stub."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            cfg_dir = os.path.join(tmp_dir, "config")
            os.makedirs(cfg_dir, exist_ok=True)
            pin_file = os.path.join(cfg_dir, "agy-mpm-core.env")
            with open(pin_file, "w") as f:
                f.write(f'AGY_MPM_PYTHON="{sys.executable}"\n')

            fake_bin = os.path.join(tmp_dir, "fake_bin")
            os.makedirs(fake_bin, exist_ok=True)
            fake_py = os.path.join(fake_bin, "python3")
            with open(fake_py, "w") as f:
                f.write("#!/bin/sh\nexit 1\n")
            os.chmod(fake_py, 0o755)

            env = {
                "AGY_CONFIG_DIR": cfg_dir,
                "PATH": f"{fake_bin}:/bin:/usr/bin",
                "AGY_MPM_PYTHON": "",
                "VIRTUAL_ENV": "",
                "CONDA_PREFIX": "",
            }
            proc = subprocess.run(
                [MPM_PY_SCRIPT, "--print-python"],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr}")
            self.assertEqual(proc.stdout.strip(), sys.executable)

    def test_ru_symlink_mpm_py(self):
        """(c) Test RU symlink ./ru/scripts/mpm-py --print-python."""
        self.assertTrue(os.path.islink(os.path.join(REPO_DIR, "ru", "scripts")))
        self.assertTrue(os.path.isfile(RU_MPM_PY_SCRIPT))
        self.assertTrue(os.access(RU_MPM_PY_SCRIPT, os.X_OK))

        proc = subprocess.run(
            [RU_MPM_PY_SCRIPT, "--print-python"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"Failed: {proc.stderr}")
        resolved = proc.stdout.strip()
        self.assertTrue(os.path.isfile(resolved))
        self.assertTrue(os.access(resolved, os.X_OK))

    def test_missing_python_fallback_force_ask_json(self):
        """(d) Test missing Python fallback emitting valid force_ask JSON for destructive-cmd-guard.py."""
        env = {
            "AGY_MPM_DISABLE_SYSTEM": "1",
            "AGY_MPM_IGNORE_PIN": "1",
            "AGY_MPM_PYTHON": "",
            "VIRTUAL_ENV": "",
            "CONDA_PREFIX": "",
            "PATH": "/bin:/usr/bin",
        }
        guard_rel = os.path.join("scripts", "destructive-cmd-guard.py")
        proc = subprocess.run(
            [MPM_PY_SCRIPT, guard_rel],
            capture_output=True,
            text=True,
            env=env,
            cwd=REPO_DIR,
        )
        self.assertEqual(proc.returncode, 0, f"Expected exit 0 for force_ask, got: {proc.returncode}, stderr: {proc.stderr}")
        data = json.loads(proc.stdout)
        self.assertEqual(data.get("decision"), "force_ask")
        self.assertIn("Python >=3.8 not found", data.get("reason", ""))
        self.assertIn("Python >=3.8 is required", proc.stderr)


class TestInstallerCli(unittest.TestCase):
    """Test suite for install.sh CLI options and life-cycle."""

    def test_lang_en_ru_status_doctor(self):
        """(a) Test --lang en, --lang ru, --status, and --doctor in isolated temp dirs."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            plugins_dir = os.path.join(tmp_dir, "plugins")
            config_dir = os.path.join(tmp_dir, "config")
            env = dict(os.environ)
            env["AGY_PLUGINS_DIR"] = plugins_dir
            env["AGY_CONFIG_DIR"] = config_dir
            env["HOME"] = tmp_dir

            # --lang en
            p_en = subprocess.run([INSTALL_SCRIPT, "--lang", "en"], capture_output=True, text=True, env=env)
            self.assertEqual(p_en.returncode, 0, p_en.stderr)
            link_path = os.path.join(plugins_dir, "agy-mpm-core")
            self.assertTrue(os.path.islink(link_path))
            self.assertEqual(os.path.realpath(link_path), os.path.realpath(REPO_DIR))

            # --lang ru
            p_ru = subprocess.run([INSTALL_SCRIPT, "--lang", "ru"], capture_output=True, text=True, env=env)
            self.assertEqual(p_ru.returncode, 0, p_ru.stderr)
            self.assertEqual(os.path.realpath(link_path), os.path.realpath(os.path.join(REPO_DIR, "ru")))

            # --status
            p_stat = subprocess.run([INSTALL_SCRIPT, "--status"], capture_output=True, text=True, env=env)
            self.assertEqual(p_stat.returncode, 0, p_stat.stderr)
            self.assertIn("INSTALLED (valid symlink)", p_stat.stdout)
            self.assertIn("Russian edition", p_stat.stdout)
            self.assertIn("Hook Guard  : ACTIVE", p_stat.stdout)

            # --doctor
            if os.environ.get("AGY_MPM_SKIP_DOCTOR_TESTS") == "1":
                # Break recursion when invoked from inside install.sh --doctor
                return

            p_doc = subprocess.run([INSTALL_SCRIPT, "--doctor"], capture_output=True, text=True, env=env)
            self.assertEqual(p_doc.returncode, 0, p_doc.stderr)
            self.assertIn("Guard Smoke   : PASS", p_doc.stdout)
            self.assertIn("Test Suite    : PASS", p_doc.stdout)
            self.assertIn("All doctor health checks passed", p_doc.stdout)

    def test_custom_python_and_uninstall(self):
        """(b) Test --python <sys.executable> and --uninstall."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            plugins_dir = os.path.join(tmp_dir, "plugins")
            config_dir = os.path.join(tmp_dir, "config")
            env = dict(os.environ)
            env["AGY_PLUGINS_DIR"] = plugins_dir
            env["AGY_CONFIG_DIR"] = config_dir
            env["HOME"] = tmp_dir

            p_inst = subprocess.run(
                [INSTALL_SCRIPT, "--lang", "en", "--python", sys.executable],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(p_inst.returncode, 0, p_inst.stderr)
            pin_file = os.path.join(config_dir, "agy-mpm-core.env")
            self.assertTrue(os.path.isfile(pin_file))
            with open(pin_file, "r") as f:
                content = f.read()
            self.assertIn(sys.executable, content)

            p_un = subprocess.run([INSTALL_SCRIPT, "--uninstall"], capture_output=True, text=True, env=env)
            self.assertEqual(p_un.returncode, 0, p_un.stderr)
            link_path = os.path.join(plugins_dir, "agy-mpm-core")
            self.assertFalse(os.path.exists(link_path))
            self.assertFalse(os.path.exists(pin_file))

    def test_migrate_and_check_projects(self):
        """(c) Test --migrate --check-projects <stale_mock_repo> flags outdated GEMINI.md & missing .agents/teamwork/."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            plugins_dir = os.path.join(tmp_dir, "plugins")
            config_dir = os.path.join(tmp_dir, "config")
            env = dict(os.environ)
            env["AGY_PLUGINS_DIR"] = plugins_dir
            env["AGY_CONFIG_DIR"] = config_dir
            env["HOME"] = tmp_dir

            stale_repo = os.path.join(tmp_dir, "stale_mock_project")
            os.makedirs(stale_repo, exist_ok=True)
            with open(os.path.join(stale_repo, ".gitignore"), "w") as f:
                f.write(".DS_Store\nnode_modules/\n")
            with open(os.path.join(stale_repo, "GEMINI.md"), "w") as f:
                f.write("# Legacy Project Adapter (v2.2.0)\n")

            p_mig = subprocess.run(
                [INSTALL_SCRIPT, "--migrate", "--check-projects", stale_repo],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(p_mig.returncode, 0, p_mig.stderr)
            self.assertIn("Missing '.agents/teamwork/' in .gitignore", p_mig.stdout)
            self.assertIn("Stale pre-v2.3 adapter in GEMINI.md", p_mig.stdout)
            self.assertIn("/kit-bootstrap --migrate", p_mig.stdout)

    def test_venv_stdlib_creation(self):
        """(d) Test --venv=stdlib creates isolated .venv quickly without network calls."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            plugins_dir = os.path.join(tmp_dir, "plugins")
            config_dir = os.path.join(tmp_dir, "config")
            env = dict(os.environ)
            env["AGY_PLUGINS_DIR"] = plugins_dir
            env["AGY_CONFIG_DIR"] = config_dir
            env["HOME"] = tmp_dir

            mock_repo = os.path.join(tmp_dir, "mock_kit")
            os.makedirs(os.path.join(mock_repo, "scripts"), exist_ok=True)
            shutil.copy(INSTALL_SCRIPT, os.path.join(mock_repo, "install.sh"))
            shutil.copy(MPM_PY_SCRIPT, os.path.join(mock_repo, "scripts", "mpm-py"))
            shutil.copy(GUARD_SCRIPT, os.path.join(mock_repo, "scripts", "destructive-cmd-guard.py"))
            shutil.copy(os.path.join(REPO_DIR, "plugin.json"), os.path.join(mock_repo, "plugin.json"))
            shutil.copy(os.path.join(REPO_DIR, "hooks.json"), os.path.join(mock_repo, "hooks.json"))

            p_venv = subprocess.run(
                [os.path.join(mock_repo, "install.sh"), "--venv=stdlib", "--no-pin"],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(p_venv.returncode, 0, p_venv.stderr)
            venv_py3 = os.path.join(mock_repo, ".venv", "bin", "python3")
            venv_py = os.path.join(mock_repo, ".venv", "bin", "python")
            self.assertTrue(os.path.exists(venv_py3) or os.path.exists(venv_py))


if __name__ == "__main__":
    unittest.main()
