#!/usr/bin/env python3
"""Shared common helpers, regex patterns, and git utilities for MPM guards.

Pure Python 3 standard library only.
"""

import os
import re
import subprocess
from typing import Dict, List, Optional, Set, Tuple

SECRET_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("OpenAI/Stripe Secret Key", re.compile(r"\bsk-[A-Za-z0-9]{10,}\b")),
    ("GitHub Personal Token", re.compile(r"\bghp_[A-Za-z0-9]{20,}\b")),
    ("AWS Access Key ID", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("NPM Access Token", re.compile(r"\bnpm_[A-Za-z0-9]{20,}\b")),
    ("Slack API Token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]+\b")),
    ("Google API Key", re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b")),
    ("Private Key Block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("Generic Bearer Token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{20,}\b")),
]

DANGEROUS_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("git clean", re.compile(r"\bgit\s+(?:-[^\s]+\s+)*clean\b")),
    ("git reset --hard", re.compile(r"\bgit\s+(?:-[^\s]+\s+)*reset\s+.*--hard\b")),
    ("git checkout worktree", re.compile(r"\bgit\s+(?:-[^\s]+\s+)*checkout\s+(?:.*--\s+|\s*\.\s*$)")),
    ("git restore worktree", re.compile(r"\bgit\s+(?:-[^\s]+\s+)*restore\b")),
    ("bare rm", re.compile(r"\brm\s+")),
]


def run_git_cmd(repo: str, args: List[str]) -> Tuple[int, str, str]:
    """Execute git command in repository directory returning (code, stdout, stderr)."""
    cmd = ["git", "-C", repo] + args
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=False)
    out = res.stdout.decode("utf-8", errors="replace")
    err = res.stderr.decode("utf-8", errors="replace")
    return res.returncode, out, err


def parse_porcelain_status(repo: str) -> Tuple[List[str], List[str], List[str]]:
    """Parse git status --porcelain -z into (modified, deleted, untracked)."""
    code, out, _ = run_git_cmd(repo, ["status", "--porcelain", "-z"])
    if code != 0:
        return [], [], []

    modified: List[str] = []
    deleted: List[str] = []
    untracked: List[str] = []

    for item in out.split("\0"):
        if not item or len(item) < 4:
            continue
        status = item[:2]
        path = item[3:].strip()
        if "->" in path:
            path = path.split("->")[-1].strip()

        if "?" in status:
            untracked.append(path)
        elif "D" in status:
            deleted.append(path)
        else:
            modified.append(path)

    return sorted(modified), sorted(deleted), sorted(untracked)


def load_baseline_files(baseline_dir: str) -> List[str]:
    """Read baseline untracked paths from baseline-untracked.txt if present."""
    txt_path = os.path.join(baseline_dir, "baseline-untracked.txt")
    if not os.path.isfile(txt_path):
        return []
    with open(txt_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def find_missing_baseline(repo: str, baseline_files: List[str], allowed: Set[str]) -> List[str]:
    """Return list of baseline files that no longer exist on disk."""
    missing: List[str] = []
    for rel_path in baseline_files:
        if rel_path in allowed:
            continue
        full_path = os.path.join(repo, rel_path)
        if not os.path.exists(full_path):
            missing.append(rel_path)
    return missing


def is_dangerous_command_text(cmd: str) -> Optional[str]:
    """Check if command text matches dangerous patterns."""
    for label, pattern in DANGEROUS_PATTERNS:
        if pattern.search(cmd):
            # For git restore, check if pure staged
            if label == "git restore worktree":
                if ("--staged" in cmd or "-S" in cmd) and "--worktree" not in cmd and "-W" not in cmd:
                    continue
            return label
    return None
