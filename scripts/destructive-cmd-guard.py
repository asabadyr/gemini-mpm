#!/usr/bin/env python3
"""PreToolUse guard script enforcing deletion shielding and destructive command bans.

Intercepts toolCall.args.CommandLine in Antigravity PreToolUse hook.
Returns JSON with decision: "allow" | "deny" | "force_ask".
Pure Python 3 standard library only.
"""

import argparse
import json
import os
import re
import shlex
import sys
import tempfile
from typing import Any, Dict, List, Optional, Set, Tuple

REASONS = {
    "en": {
        "git_clean": "Hard blocked: git clean can permanently delete uncommitted files.",
        "git_reset": "Hard blocked: git reset --hard/--merge destroys local working tree state.",
        "git_checkout": "Hard blocked: git checkout pathspec/HEAD reverts working tree files.",
        "git_restore": "Hard blocked: git restore without pure --staged modifies working tree.",
        "git_push_main": "Hard blocked: force push to main/master branch is strictly forbidden.",
        "git_push_force": "Force push detected: requires explicit confirmation.",
        "rm_catastrophic": "Hard blocked: catastrophic recursive removal targeting root/working tree.",
        "rm_outside_scratch": "Deletion requires confirmation: targets outside scratch or temp directory.",
        "rm_find_delete": "find with -delete requires explicit confirmation.",
        "python_deletion": "Inline Python deletion call requires explicit confirmation.",
        "parse_failure": "Command line could not be verified safely; confirmation required.",
    },
    "ru": {
        "git_clean": "Заблокировано: git clean может безвозвратно удалить незакоммиченные файлы.",
        "git_reset": "Заблокировано: git reset --hard/--merge уничтожает рабочее дерево.",
        "git_checkout": "Заблокировано: git checkout отменяет локальные изменения файлов.",
        "git_restore": "Заблокировано: git restore без флага --staged изменяет рабочее дерево.",
        "git_push_main": "Заблокировано: форс-пуш в ветку main/master строго запрещен.",
        "git_push_force": "Обнаружен форс-пуш: требуется подтверждение пользователя.",
        "rm_catastrophic": "Заблокировано: катастрофическое удаление корня или рабочего дерева.",
        "rm_outside_scratch": "Удаление требует подтверждения: цели вне scratch или temp.",
        "rm_find_delete": "Команда find с -delete требует подтверждения пользователя.",
        "python_deletion": "Вызов удаления через Python требует подтверждения пользователя.",
        "parse_failure": "Команда не может быть проверена безопасно; требуется подтверждение.",
    },
}

WRAPPERS = {"sudo", "time", "nohup", "command", "builtin"}
SHELL_WRAPPERS = {"sh", "bash", "zsh"}
DANGEROUS_PYTHON = ("os.remove", "os.unlink", "shutil.rmtree", ".unlink(")


def get_reason(key: str, lang: str) -> str:
    """Return localized reason message for key."""
    lang_dict = REASONS.get(lang, REASONS["en"])
    return lang_dict.get(key, REASONS["en"].get(key, "Operation requires confirmation."))


def split_shell_statements(cmd_str: str) -> List[str]:
    """Split shell command line into individual statements outside quotes."""
    statements: List[str] = []
    current: List[str] = []
    in_single = False
    in_double = False
    escaped = False
    i = 0
    length = len(cmd_str)

    while i < length:
        ch = cmd_str[i]
        if escaped:
            current.append(ch)
            escaped = False
            i += 1
            continue

        if ch == "\\" and not in_single:
            escaped = True
            current.append(ch)
            i += 1
            continue

        if ch == "'" and not in_double:
            in_single = not in_single
            current.append(ch)
            i += 1
            continue

        if ch == '"' and not in_single:
            in_double = not in_double
            current.append(ch)
            i += 1
            continue

        if not in_single and not in_double:
            if ch in (";", "\n"):
                stmt = "".join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
                i += 1
                continue
            if cmd_str.startswith("&&", i) or cmd_str.startswith("||", i):
                stmt = "".join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
                i += 2
                continue
            if ch == "|" and not cmd_str.startswith("||", i):
                stmt = "".join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
                i += 1
                continue

        current.append(ch)
        i += 1

    last_stmt = "".join(current).strip()
    if last_stmt:
        statements.append(last_stmt)
    return statements


def unwrap_command_tokens(tokens: List[str]) -> Tuple[List[str], Optional[str]]:
    """Unwrap env vars, sudo, time, command, and handle shell -c strings."""
    idx = 0
    while idx < len(tokens):
        tok = tokens[idx]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=.*", tok):
            idx += 1
            continue
        if tok in WRAPPERS:
            idx += 1
            while idx < len(tokens) and tokens[idx].startswith("-"):
                idx += 1
            continue
        if tok == "env":
            idx += 1
            while idx < len(tokens):
                t = tokens[idx]
                if t.startswith("-") or re.match(r"^[A-Za-z_][A-Za-z0-9_]*=.*", t):
                    idx += 1
                else:
                    break
            continue
        break

    remaining = tokens[idx:]
    if not remaining:
        return [], None

    cmd_name = os.path.basename(remaining[0])
    if cmd_name in SHELL_WRAPPERS and len(remaining) >= 3 and "-c" in remaining:
        c_idx = remaining.index("-c")
        if c_idx + 1 < len(remaining):
            return [], remaining[c_idx + 1]

    return remaining, None


def unwrap_git_subcommand(tokens: List[str]) -> Tuple[Optional[str], List[str]]:
    """Extract git subcommand and its arguments after skipping git flags."""
    idx = 1
    while idx < len(tokens):
        tok = tokens[idx]
        if tok in ("-C", "-c", "--git-dir", "--work-tree"):
            idx += 2
            continue
        if tok.startswith(("-C", "--git-dir=", "--work-tree=", "-c")):
            idx += 1
            continue
        if tok.startswith("-"):
            idx += 1
            continue
        return tok, tokens[idx + 1 :]
    return None, []


def check_git_clean(args: List[str]) -> Optional[str]:
    """Check git clean arguments. Return reason key on deny, None if safe."""
    is_dry_run = False
    has_force = False

    for arg in args:
        if arg in ("-n", "--dry-run"):
            is_dry_run = True
        elif arg in ("-f", "--force"):
            has_force = True
        elif arg.startswith("-") and not arg.startswith("--"):
            if "n" in arg:
                is_dry_run = True
            if "f" in arg:
                has_force = True

    if is_dry_run and not has_force:
        return None
    return "git_clean"


def check_git_reset(args: List[str]) -> Optional[str]:
    """Check git reset arguments for hard/merge resets."""
    for arg in args:
        if arg in ("--hard", "--merge"):
            return "git_reset"
    return None


def check_git_checkout(args: List[str]) -> Optional[str]:
    """Check git checkout arguments for destructive worktree reverts."""
    if "--" in args:
        return "git_checkout"
    if "." in args or "./" in args:
        return "git_checkout"
    if "HEAD" in args and len(args) > 1:
        return "git_checkout"
    return None


def check_git_restore(args: List[str]) -> Optional[str]:
    """Check git restore arguments. Only pure --staged without worktree is allowed."""
    has_staged = any(a in ("--staged", "-S") for a in args)
    has_worktree = any(a in ("--worktree", "-W") for a in args)
    if has_staged and not has_worktree:
        return None
    return "git_restore"


def check_git_push(args: List[str]) -> Tuple[Optional[str], Optional[str]]:
    """Check git push for force flags. Returns (decision, reason_key)."""
    has_force = any(
        a in ("-f", "--force", "--force-with-lease")
        or (a.startswith("-") and not a.startswith("--") and "f" in a)
        for a in args
    )
    if not has_force:
        return None, None

    targets_main = any(a in ("main", "master", "origin/main", "origin/master") for a in args)
    if targets_main:
        return "deny", "git_push_main"
    return "force_ask", "git_push_force"


def check_git_command(tokens: List[str]) -> Tuple[Optional[str], Optional[str]]:
    """Analyze git command tokens. Returns (decision, reason_key) or (None, None)."""
    subcmd, subargs = unwrap_git_subcommand(tokens)
    if not subcmd:
        return None, None

    if subcmd == "clean":
        r = check_git_clean(subargs)
        if r:
            return "deny", r
    elif subcmd == "reset":
        r = check_git_reset(subargs)
        if r:
            return "deny", r
    elif subcmd == "checkout":
        r = check_git_checkout(subargs)
        if r:
            return "deny", r
    elif subcmd == "restore":
        r = check_git_restore(subargs)
        if r:
            return "deny", r
    elif subcmd == "push":
        return check_git_push(subargs)

    return None, None


def resolve_allowed_dirs(payload: Dict[str, Any]) -> Tuple[List[str], Optional[str]]:
    """Compute (safe scratch/temp dirs, optional brain_root for sibling scratch)."""
    allowed: Set[str] = set()
    brain_root: Optional[str] = None

    art_dir = payload.get("artifactDirectoryPath")
    if art_dir:
        art_abs = os.path.abspath(art_dir)
        allowed.add(art_abs)
        allowed.add(os.path.join(art_abs, "scratch"))
        parent = os.path.dirname(art_abs)
        if os.path.basename(parent) == "brain":
            brain_root = os.path.realpath(parent)
            allowed.add(os.path.join(os.path.dirname(parent), "scratch"))

    trans_path = payload.get("transcriptPath")
    if trans_path:
        p1 = os.path.abspath(os.path.dirname(trans_path))
        p2 = os.path.abspath(os.path.dirname(p1))
        allowed.add(os.path.join(p1, "scratch"))
        allowed.add(os.path.join(p2, "scratch"))
        cur = p2
        for _ in range(3):
            parent = os.path.dirname(cur)
            if os.path.basename(parent) == "brain":
                brain_root = brain_root or os.path.realpath(parent)
                allowed.add(os.path.join(os.path.dirname(parent), "scratch"))
                break
            cur = parent

    for sys_tmp in ("/tmp", "/private/tmp", "/var/tmp", tempfile.gettempdir()):
        if os.path.exists(sys_tmp):
            allowed.add(os.path.realpath(os.path.abspath(sys_tmp)))

    real_allowed = [os.path.realpath(d) for d in allowed]
    return real_allowed, brain_root


def is_path_inside_allowed(
    target: str, cwd: str, allowed_dirs: List[str], brain_root: Optional[str] = None
) -> bool:
    """Check if target resolves inside allowed_dirs or <brain>/<uuid>/scratch/*."""
    if any(ch in target for ch in ("*", "?", "[", "]")) or "$" in target:
        return False

    abs_path = target if os.path.isabs(target) else os.path.join(cwd, target)
    norm_path = os.path.realpath(os.path.abspath(abs_path))

    for base in allowed_dirs:
        try:
            rel = os.path.relpath(norm_path, base)
            if not rel.startswith("..") and rel != ".":
                return True
        except ValueError:
            continue

    if brain_root:
        try:
            rel_brain = os.path.relpath(norm_path, brain_root)
            parts = rel_brain.split(os.sep)
            if len(parts) >= 3 and not parts[0].startswith("..") and parts[1] == "scratch":
                return True
        except ValueError:
            pass
    return False


def check_rm_targets(
    args: List[str], cwd: str, allowed_dirs: List[str], brain_root: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """Audit rm arguments and paths for catastrophic deletes or non-scratch paths."""
    targets = [a for a in args if not a.startswith("-") and a != "--"]
    if not targets:
        return "force_ask", "rm_outside_scratch"

    for t in targets:
        if t in ("/", "~", ".", "..", "*", "/*") or t.strip() in ("", "/"):
            return "deny", "rm_catastrophic"

    for t in targets:
        if not is_path_inside_allowed(t, cwd, allowed_dirs, brain_root):
            return "force_ask", "rm_outside_scratch"

    return None, None


def check_python_inline(tokens: List[str], raw_stmt: str) -> Tuple[Optional[str], Optional[str]]:
    """Audit python inline scripts for deletion methods."""
    cmd_name = os.path.basename(tokens[0])
    if cmd_name.startswith("python"):
        for dang in DANGEROUS_PYTHON:
            if dang in raw_stmt:
                return "force_ask", "python_deletion"
    return None, None


def evaluate_single_statement(
    stmt: str, cwd: str, allowed_dirs: List[str], brain_root: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """Evaluate one shell statement. Returns (decision, reason_key) or (None, None)."""
    try:
        tokens = shlex.split(stmt, posix=True)
    except Exception:
        return "force_ask", "parse_failure"

    if not tokens:
        return None, None

    unwrapped, sub_cmd = unwrap_command_tokens(tokens)
    if sub_cmd is not None:
        return evaluate_command_line(sub_cmd, cwd, allowed_dirs, brain_root)

    if not unwrapped:
        return None, None

    base_cmd = os.path.basename(unwrapped[0])

    if base_cmd == "git":
        return check_git_command(unwrapped)

    if base_cmd in ("rm", "rmdir", "unlink", "shred"):
        return check_rm_targets(unwrapped[1:], cwd, allowed_dirs, brain_root)

    if base_cmd == "find" and "-delete" in unwrapped:
        return "force_ask", "rm_find_delete"

    py_dec, py_reason = check_python_inline(unwrapped, stmt)
    if py_dec:
        return py_dec, py_reason

    return None, None


def evaluate_command_line(
    cmd_str: str, cwd: str, allowed_dirs: List[str], brain_root: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """Evaluate whole command line by splitting statements and checking each."""
    statements = split_shell_statements(cmd_str)
    for stmt in statements:
        dec, reason_key = evaluate_single_statement(stmt, cwd, allowed_dirs, brain_root)
        if dec == "deny":
            return "deny", reason_key
        if dec == "force_ask":
            return "force_ask", reason_key
    return None, None


def process_hook(payload: Dict[str, Any], lang: str) -> Dict[str, str]:
    """Process PreToolUse payload and generate decision dictionary."""
    tool_call = payload.get("toolCall", {})
    if tool_call.get("name") != "run_command":
        return {"decision": "allow"}

    args = tool_call.get("args", {})
    cmd_line = args.get("CommandLine", "")
    if not cmd_line or not isinstance(cmd_line, str):
        return {"decision": "allow"}

    cwd = payload.get("cwd", os.getcwd())
    allowed_dirs, brain_root = resolve_allowed_dirs(payload)

    dec, reason_key = evaluate_command_line(cmd_line, cwd, allowed_dirs, brain_root)
    if dec and reason_key:
        return {"decision": dec, "reason": get_reason(reason_key, lang)}

    return {"decision": "allow"}


def main() -> None:
    """Read PreToolUse JSON payload from stdin, audit command, emit JSON result."""
    parser = argparse.ArgumentParser(description="Antigravity PreToolUse Deletion Shield")
    parser.add_argument("--lang", choices=["en", "ru"], default="en", help="Language for reason string")
    cli_args = parser.parse_args()

    try:
        raw_input = sys.stdin.read()
        payload = json.loads(raw_input) if raw_input.strip() else {}
        result = process_hook(payload, cli_args.lang)
    except Exception as exc:
        result = {
            "decision": "force_ask",
            "reason": f"Safety check failed: {exc}",
        }

    sys.stdout.write(json.dumps(result) + "\n")
    sys.stdout.flush()
    sys.exit(0)


if __name__ == "__main__":
    main()
