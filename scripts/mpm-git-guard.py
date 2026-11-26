#!/usr/bin/env python3
"""MPM Git Guard: Snapshot, audit, restore, and secret scanning for multi-agent workflows.

Subcommands:
  snapshot     Capture pre-wave baseline (untracked files, modified files, stash, metadata).
  audit        Detect tracked/untracked deletions, missing baseline files, or dangerous tool calls.
  restore      Recover deleted files from baseline tarball without clobbering new work.
  secret-scan  Audit changed files for secret and credential patterns.

Pure Python 3 standard library only.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tarfile
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure scripts directory is on sys.path for guard_common
SCRIPTS_DIR = os.path.abspath(os.path.dirname(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from guard_common import (  # noqa: E402
    SECRET_PATTERNS,
    DANGEROUS_PATTERNS,
    run_git_cmd as run_git,
    parse_porcelain_status,
    load_baseline_files as load_baseline_untracked,
    find_missing_baseline as check_missing_untracked,
)


def verify_git_repo(repo: str) -> None:
    """Verify repo directory is a valid git repository or exit with error."""
    if not os.path.isdir(repo):
        sys.stderr.write(f"Error: Repository directory '{repo}' does not exist.\n")
        sys.exit(1)
    code, out, _ = run_git(repo, ["rev-parse", "--is-inside-work-tree"])
    if code != 0 or out.strip() != "true":
        sys.stderr.write(f"Error: '{repo}' is not inside a git work tree.\n")
        sys.exit(1)


def get_git_head_and_branch(repo: str) -> Tuple[Optional[str], str]:
    """Get HEAD commit SHA (or None if 0 commits) and current branch name."""
    code, out, _ = run_git(repo, ["rev-parse", "--verify", "HEAD"])
    head_sha = out.strip() if code == 0 else None

    code_br, out_br, _ = run_git(repo, ["symbolic-ref", "--short", "HEAD"])
    branch = out_br.strip() if code_br == 0 else "HEAD"
    return head_sha, branch


def get_untracked_files(repo: str) -> List[str]:
    """Get list of untracked non-ignored files in repository."""
    cmd = ["git", "-C", repo, "ls-files", "--others", "--exclude-standard", "-z"]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    raw = res.stdout.split(b"\0")
    files: List[str] = []
    for item in raw:
        decoded = item.decode("utf-8", errors="replace").strip()
        if decoded:
            files.append(decoded)
    files.sort()
    return files


def get_modified_tracked_files(repo: str) -> List[str]:
    """Get list of tracked files that are currently modified or staged on disk."""
    modified, _, _ = parse_porcelain_status(repo)
    return [p for p in modified if os.path.exists(os.path.join(repo, p))]


def build_backup_tarball(repo: str, files_to_backup: List[str], tar_path: str) -> int:
    """Archive specified relative paths into a compressed tarball."""
    count = 0
    with tarfile.open(tar_path, "w:gz") as tar:
        for rel_path in files_to_backup:
            full_path = os.path.join(repo, rel_path)
            if os.path.exists(full_path):
                tar.add(full_path, arcname=rel_path, recursive=False)
                count += 1
    return count


def cmd_snapshot(args: argparse.Namespace) -> None:
    """Create a pre-wave baseline backup with untracked/modified files and metadata."""
    repo = os.path.abspath(args.repo)
    out_dir = os.path.abspath(args.out)
    verify_git_repo(repo)
    os.makedirs(out_dir, exist_ok=True)

    head_sha, branch = get_git_head_and_branch(repo)
    untracked = get_untracked_files(repo)
    modified = get_modified_tracked_files(repo)

    stash_sha: Optional[str] = None
    if head_sha:
        code, out, _ = run_git(repo, ["stash", "create"])
        if code == 0 and out.strip():
            stash_sha = out.strip()

    untracked_txt_path = os.path.join(out_dir, "baseline-untracked.txt")
    with open(untracked_txt_path, "w", encoding="utf-8") as f:
        for p in untracked:
            f.write(p + "\n")

    combined_files = sorted(list(set(untracked + modified)))
    tar_path = os.path.join(out_dir, "pre-wave-backup.tar.gz")
    archived_count = build_backup_tarball(repo, combined_files, tar_path)

    _, status_out, _ = run_git(repo, ["status", "--short"])
    meta = {
        "repo": repo,
        "head": head_sha,
        "branch": branch,
        "stash_sha": stash_sha,
        "untracked_count": len(untracked),
        "modified_count": len(modified),
        "archived_count": archived_count,
        "status_lines": [line for line in status_out.splitlines() if line.strip()],
    }

    meta_path = os.path.join(out_dir, "baseline-meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"[SNAPSHOT] Baseline created in {out_dir}")
    print(f"  Head: {head_sha or '0-commit (EMPTY)'} | Branch: {branch}")
    print(f"  Untracked: {len(untracked)} | Modified: {len(modified)} | Archived: {archived_count}")
    if stash_sha:
        print(f"  Stash SHA: {stash_sha}")


def check_tracked_deletions(repo: str, allowed: Set[str]) -> List[str]:
    """Scan git status for tracked deletions not covered by allowed list."""
    _, deleted, _ = parse_porcelain_status(repo)
    return [p for p in deleted if p not in allowed]


def check_transcript_commands(transcript_path: str) -> List[Dict[str, str]]:
    """Scan recent run_command tool calls in transcript for dangerous patterns."""
    hits: List[Dict[str, str]] = []
    if not os.path.isfile(transcript_path):
        return hits

    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return hits

    for line in lines[-50:]:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except Exception:
            continue
        calls = entry.get("tool_calls", [])
        for call in calls:
            cmd = call.get("args", {}).get("CommandLine", "")
            for label, pattern in DANGEROUS_PATTERNS:
                if pattern.search(cmd):
                    hits.append({"pattern": label, "command": cmd})
    return hits


def cmd_audit(args: argparse.Namespace) -> None:
    """Audit working tree against baseline for deletions and missing files."""
    repo = os.path.abspath(args.repo)
    baseline_dir = os.path.abspath(args.baseline)
    verify_git_repo(repo)

    allowed = set(args.allowed_deletes or [])
    baseline_untracked = load_baseline_untracked(baseline_dir)

    deleted_tracked = check_tracked_deletions(repo, allowed)
    missing_untracked = check_missing_untracked(repo, baseline_untracked, allowed)

    transcript_hits: List[Dict[str, str]] = []
    if args.transcript:
        transcript_hits = check_transcript_commands(os.path.abspath(args.transcript))

    is_clean = not deleted_tracked and not missing_untracked and not transcript_hits
    report = {
        "status": "PASS" if is_clean else "FAIL",
        "deleted_tracked": deleted_tracked,
        "missing_untracked": missing_untracked,
        "transcript_hits": transcript_hits,
    }

    print(json.dumps(report, indent=2))
    if not is_clean:
        print("\n[FAIL] Deletions or dangerous operations detected!", file=sys.stderr)
        if deleted_tracked:
            print(f"  Tracked deletions: {deleted_tracked}", file=sys.stderr)
        if missing_untracked:
            print(f"  Missing baseline files: {missing_untracked}", file=sys.stderr)
        if transcript_hits:
            print(f"  Dangerous commands in transcript: {len(transcript_hits)}", file=sys.stderr)
        sys.exit(2)

    print("\n[PASS] Working tree audit clean: zero unapproved deletions.", file=sys.stdout)
    sys.exit(0)


def cmd_restore(args: argparse.Namespace) -> None:
    """Restore deleted files from baseline tarball."""
    repo = os.path.abspath(args.repo)
    baseline_dir = os.path.abspath(args.baseline)
    tar_path = os.path.join(baseline_dir, "pre-wave-backup.tar.gz")

    if not os.path.isfile(tar_path):
        sys.stderr.write(f"Error: Baseline archive '{tar_path}' not found.\n")
        sys.exit(1)

    restored = 0
    with tarfile.open(tar_path, "r:gz") as tar:
        for member in tar.getmembers():
            dest = os.path.join(repo, member.name)
            if args.only_missing and os.path.exists(dest):
                continue
            if sys.version_info >= (3, 12):
                tar.extract(member, path=repo, filter="data")
            else:
                tar.extract(member, path=repo)
            restored += 1

    mode_str = "missing only" if args.only_missing else "forced overwrite"
    print(f"[RESTORE] Successfully restored {restored} files ({mode_str}) into {repo}")


def cmd_secret_scan(args: argparse.Namespace) -> None:
    """Scan given files for secret and credential patterns."""
    repo = os.path.abspath(args.repo)
    findings: List[Tuple[str, int, str]] = []

    for rel_path in args.files:
        full_path = rel_path if os.path.isabs(rel_path) else os.path.join(repo, rel_path)
        if not os.path.isfile(full_path):
            continue
        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                for line_no, line in enumerate(f, start=1):
                    for label, pattern in SECRET_PATTERNS:
                        if pattern.search(line):
                            findings.append((rel_path, line_no, label))
        except Exception as exc:
            sys.stderr.write(f"Warning: Could not scan {rel_path}: {exc}\n")

    if findings:
        print("[FAIL] Potential secrets detected:")
        for path, line_no, label in findings:
            print(f"  {path}:{line_no} [{label}]")
        sys.exit(1)

    print("[PASS] Secret scan clean: zero detected credential patterns.")
    sys.exit(0)


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser for git-guard subcommands."""
    parser = argparse.ArgumentParser(description="MPM Git Guard & Deletion Shield")
    subparsers = parser.add_subparsers(dest="command", required=True)

    snap = subparsers.add_parser("snapshot", help="Create pre-wave baseline backup")
    snap.add_argument("--repo", required=True, help="Repository root directory")
    snap.add_argument("--out", required=True, help="Output scratch directory")

    audit = subparsers.add_parser("audit", help="Audit working tree against baseline")
    audit.add_argument("--repo", required=True, help="Repository root directory")
    audit.add_argument("--baseline", required=True, help="Baseline directory containing snapshot")
    audit.add_argument("--allowed-deletes", nargs="*", help="File paths approved for deletion")
    audit.add_argument("--transcript", help="Path to transcript.jsonl for command auditing")

    restore = subparsers.add_parser("restore", help="Restore files from baseline backup")
    restore.add_argument("--repo", required=True, help="Repository root directory")
    restore.add_argument("--baseline", required=True, help="Baseline directory containing snapshot")
    restore.add_argument("--only-missing", action="store_true", default=True, help="Restore only missing files (default)")
    restore.add_argument("--force", dest="only_missing", action="store_false", help="Force overwrite existing files")

    scan = subparsers.add_parser("secret-scan", help="Scan specified files for secrets")
    scan.add_argument("--repo", required=True, help="Repository root directory")
    scan.add_argument("--files", nargs="+", required=True, help="File paths to scan")

    return parser


def main() -> None:
    """Main CLI entrypoint for mpm-git-guard."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "snapshot":
        cmd_snapshot(args)
    elif args.command == "audit":
        cmd_audit(args)
    elif args.command == "restore":
        cmd_restore(args)
    elif args.command == "secret-scan":
        cmd_secret_scan(args)


if __name__ == "__main__":
    main()
