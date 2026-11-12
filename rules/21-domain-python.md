---
trigger: glob
globs: "**/*.py, **/pyproject.toml"
description: "Python engineering guardrails: uv/ruff/mypy toolchain, import-time purity, async timeout safety, runtime invariant checks, and mutable-default traps."
---

# Domain Pack: Python (`21`)

## Critical Python Guardrails
| Area | Trap | Mandatory Practice |
|---|---|---|
| **Environment & Runner** | Running global `python`/`pytest` outside project venv or installing ad-hoc packages | Respect repo toolchain (`uv run`, `poetry run`, or `.venv/bin/pytest`); verify `pyproject.toml` config before running `ruff` / `mypy` / `pytest` |
| **Import-Time Purity (`🔴`)** | Creating DB engines, HTTP clients, `boto3`/cloud sessions, or reading missing env vars at module import | Defer initialization to explicit startup lifespans, factory functions, or lazy dependency providers |
| **Security / Prod Invariants (`🔴`)** | Using bare `assert user.is_admin` for auth, validation, or data integrity | `python -O` strips `assert` statements! Raise explicit typed exceptions (`ValueError`, `PermissionError`, domain errors) or use `icontract` / Pydantic validators |
| **Async & I/O Timeouts (`🔴`)** | Unbounded `httpx` / `aiohttp` / subprocess calls or blocking sync I/O inside `async def` | Enforce explicit timeouts (`httpx.Timeout`, `asyncio.wait_for`), offload blocking CPU/disk calls via `asyncio.to_thread`, and store references to background `asyncio.create_task` objects |
| **Mutable Defaults & Closures** | `def f(items: list[str] = []):` or late-binding loop variables in lambdas | Use `None` sentinel (`items: list[str] | None = None`) or `dataclasses.field(default_factory=list)`; bind loop vars explicitly |
| **Exception Hygiene** | Bare `except:` or swallowing `BaseException` (`CancelledError`, `KeyboardInterrupt`) | Catch narrow `Exception` subclasses, preserve tracebacks with `raise NewError(...) from err`, and never silence errors without structured context |
| **Typing & Docstrings** | `Any` leakage across module boundaries or `HOW`-heavy prose docstrings | Annotate public signatures strictly; document **WHAT** (contract, units, raised errors) and **WHY** (constraints) |
