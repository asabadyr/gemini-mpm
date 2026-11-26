#!/usr/bin/env python3
"""MPM Live Watch: Zero-token continuous OS watchdog for subagent transcripts and repo state.

Monitors active transcript.jsonl files and working tree state every --interval seconds.
Exits immediately with JSON alert and specific exit code on anomaly:
  10: DELETION_DETECTED (tracked deletion or missing baseline file)
  11: DANGEROUS_COMMAND (destructive command attempted)
  12: ERROR_LOOP (consecutive tool/stream errors)
  13: READ_ONLY_TILT (consecutive read_file-only turns)
  14: IDLE_COMA (no transcript growth within --stale-sec)
  15: SCOPE_ESCAPE (unapproved edit outside --scope)

Pure Python 3 standard library only.
"""

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure scripts directory is on sys.path for guard_common
SCRIPTS_DIR = os.path.abspath(os.path.dirname(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from guard_common import (  # noqa: E402
    find_missing_baseline,
    is_dangerous_command_text,
    load_baseline_files,
    parse_porcelain_status,
)

EXIT_DELETION = 10
EXIT_DANGEROUS_CMD = 11
EXIT_ERROR_LOOP = 12
EXIT_READ_TILT = 13
EXIT_IDLE_COMA = 14
EXIT_SCOPE_ESCAPE = 15

ERROR_SUBSTRINGS = (
    "The stream was interrupted",
    "tool call denied by pre-tool hook",
    "tool call denied",
)


def emit_alert(code: int, alert_type: str, details: Dict[str, Any]) -> None:
    """Print structured JSON alert to stdout and exit with code."""
    payload = {
        "alert": alert_type,
        "exit_code": code,
        "timestamp": time.time(),
        "details": details,
    }
    sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    sys.stdout.flush()
    sys.exit(code)


class TranscriptWatcher:
    """Tracks byte offset and tilt metrics for a single transcript.jsonl file."""

    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        self.offset = 0
        self.last_growth_time = time.time()
        self.consecutive_errors = 0
        self.consecutive_reads = 0
        self.is_completed = False

    def update_completion_state(self, entry: Dict[str, Any]) -> None:
        """Track whether the subagent finished its turn cleanly (idle) or resumed."""
        step_type = entry.get("type")
        status = entry.get("status")
        tool_calls = entry.get("tool_calls", [])
        if step_type == "PLANNER_RESPONSE" and status == "DONE" and not tool_calls:
            self.is_completed = True
        elif tool_calls or step_type in ("SYSTEM_MESSAGE", "USER_INPUT"):
            self.is_completed = False

    def check_file_growth(self) -> List[Dict[str, Any]]:
        """Read newly appended lines from transcript file."""
        if not os.path.isfile(self.path):
            return []

        curr_size = os.path.getsize(self.path)
        if curr_size > self.offset:
            self.last_growth_time = time.time()

        new_entries: List[Dict[str, Any]] = []
        with open(self.path, "r", encoding="utf-8", errors="replace") as f:
            f.seek(self.offset)
            for line in f:
                line = line.strip()
                if line:
                    try:
                        new_entries.append(json.loads(line))
                    except Exception:
                        continue
            self.offset = f.tell()
        return new_entries

    def audit_step_errors(self, entry: Dict[str, Any], max_errors: int) -> None:
        """Check for error status or stream interruption strings."""
        is_err = entry.get("status") == "ERROR"
        content = str(entry.get("content", ""))
        thinking = str(entry.get("thinking", ""))

        for sub in ERROR_SUBSTRINGS:
            if sub in content or sub in thinking:
                is_err = True
                break

        if is_err:
            self.consecutive_errors += 1
            if self.consecutive_errors >= max_errors:
                emit_alert(
                    EXIT_ERROR_LOOP,
                    "ERROR_LOOP",
                    {"path": self.path, "consecutive_errors": self.consecutive_errors},
                )
        else:
            self.consecutive_errors = 0

    def audit_step_commands_and_reads(self, entry: Dict[str, Any], read_tilt_cap: int) -> None:
        """Inspect tool calls for dangerous commands and read_file tilt."""
        tool_calls = entry.get("tool_calls", [])
        if not tool_calls:
            return

        tool_names = [call.get("name") for call in tool_calls]

        for call in tool_calls:
            if call.get("name") == "run_command":
                cmd = call.get("args", {}).get("CommandLine", "")
                dang = is_dangerous_command_text(cmd)
                if dang:
                    emit_alert(
                        EXIT_DANGEROUS_CMD,
                        "DANGEROUS_COMMAND",
                        {"path": self.path, "command": cmd, "pattern": dang},
                    )

        if all(name == "read_file" for name in tool_names):
            self.consecutive_reads += 1
            if self.consecutive_reads >= read_tilt_cap:
                emit_alert(
                    EXIT_READ_TILT,
                    "READ_ONLY_TILT",
                    {"path": self.path, "consecutive_reads": self.consecutive_reads},
                )
        else:
            self.consecutive_reads = 0


def load_baseline_modified(baseline_dir: str) -> Set[str]:
    """Load pre-existing modified paths from baseline-meta.json if present."""
    meta_path = os.path.join(baseline_dir, "baseline-meta.json")
    if not os.path.isfile(meta_path):
        return set()
    try:
        meta = json.load(open(meta_path, "r", encoding="utf-8"))
        paths: Set[str] = set()
        for line in meta.get("status_lines", []):
            if len(line) >= 4 and line[:2] != "??":
                p = line[3:].strip()
                if " -> " in p:
                    p = p.split(" -> ", 1)[1].strip()
                paths.add(p)
        return paths
    except Exception:
        return set()


def audit_repository_state(
    repo: str,
    baseline_dir: Optional[str],
    allowed_scope: Optional[Set[str]],
    baseline_files: List[str],
    baseline_modified: Set[str],
) -> None:
    """Verify repo has no tracked deletions, missing baseline files, or scope escapes."""
    if not repo or not os.path.isdir(repo):
        return

    modified, deleted, untracked = parse_porcelain_status(repo)

    if deleted:
        emit_alert(EXIT_DELETION, "DELETION_DETECTED", {"deleted_tracked": deleted})

    if baseline_dir:
        missing = find_missing_baseline(repo, baseline_files, set())
        if missing:
            emit_alert(EXIT_DELETION, "DELETION_DETECTED", {"missing_baseline": missing})

    if allowed_scope is not None:
        scope_violations: List[str] = []
        for path in modified:
            if path not in allowed_scope and path not in baseline_modified:
                scope_violations.append(path)
        if scope_violations:
            emit_alert(
                EXIT_SCOPE_ESCAPE,
                "SCOPE_ESCAPE",
                {"scope_violations": scope_violations, "allowed_scope": sorted(list(allowed_scope))},
            )


def run_watch_loop(args: argparse.Namespace) -> None:
    """Continuous polling loop auditing transcripts and git working tree."""
    watchers = [TranscriptWatcher(p) for p in (args.transcripts or [])]
    baseline_files: List[str] = []
    baseline_modified: Set[str] = set()
    if args.baseline:
        base_abs = os.path.abspath(args.baseline)
        baseline_files = load_baseline_files(base_abs)
        baseline_modified = load_baseline_modified(base_abs)

    allowed_scope: Optional[Set[str]] = None
    if args.scope is not None:
        allowed_scope = set(args.scope)

    start_time = time.time()

    while True:
        now = time.time()
        if args.max_runtime > 0 and (now - start_time) >= args.max_runtime:
            sys.exit(0)

        for w in watchers:
            new_steps = w.check_file_growth()
            for step in new_steps:
                w.update_completion_state(step)
                w.audit_step_errors(step, args.max_errors)
                w.audit_step_commands_and_reads(step, args.read_tilt)

            if not w.is_completed and (now - w.last_growth_time) > args.stale_sec:
                emit_alert(
                    EXIT_IDLE_COMA,
                    "IDLE_COMA",
                    {"path": w.path, "idle_seconds": round(now - w.last_growth_time, 1)},
                )

        if args.repo:
            audit_repository_state(
                os.path.abspath(args.repo), args.baseline, allowed_scope, baseline_files, baseline_modified
            )

        time.sleep(args.interval)


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for mpm-live-watch."""
    parser = argparse.ArgumentParser(description="MPM Live Watch OS Continuous Monitor")
    parser.add_argument("--transcript", dest="transcripts", action="append", help="Path to transcript.jsonl")
    parser.add_argument("--repo", help="Target git repository directory")
    parser.add_argument("--baseline", help="Directory containing baseline-untracked.txt")
    parser.add_argument("--interval", type=float, default=1.5, help="Polling interval in seconds")
    parser.add_argument("--stale-sec", type=float, default=180.0, help="Max seconds without growth")
    parser.add_argument("--read-tilt", type=int, default=10, help="Max consecutive read_file turns")
    parser.add_argument("--max-errors", type=int, default=2, help="Max consecutive errors before alert")
    parser.add_argument("--scope", nargs="*", help="Allowed file paths for edits")
    parser.add_argument("--max-runtime", type=float, default=0.0, help="Max runtime in seconds (0=infinite)")
    return parser


def main() -> None:
    """Entry point for live watch loop."""
    parser = build_parser()
    args = parser.parse_args()
    run_watch_loop(args)


if __name__ == "__main__":
    main()
