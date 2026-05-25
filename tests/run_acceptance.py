"""Drive each hook with a sample payload and assert the expected exit code.

Run from the repo root:
    py tests/run_acceptance.py

Exit 0 if all cases pass, 1 otherwise. Prints a single line per case.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO     = Path(__file__).resolve().parent.parent
HOOKS    = REPO / "hooks"

# Resolve a Python interpreter that can run the hooks
PYTHON   = shutil.which("py") or shutil.which("python") or sys.executable


def run(hook: str, payload: Dict[str, Any]) -> Tuple[int, str, str]:
    res = subprocess.run(
        [PYTHON, str(HOOKS / f"{hook}.py")],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=15,
    )
    return res.returncode, res.stdout, res.stderr


def assert_exit(case: str, expected: int, got: int, stderr: str) -> bool:
    ok = got == expected
    flag = "OK   " if ok else "FAIL "
    extra = "" if ok else f" (got {got}, expected {expected})"
    print(f"{flag} {case}{extra}")
    if not ok and stderr:
        for line in stderr.strip().splitlines():
            print(f"        | {line}")
    return ok


def main() -> int:
    cases: List[Tuple[str, str, Dict[str, Any], int]] = [
        # ---- pre_commit_no_ai_trailer ----
        ("pre_commit: Co-Authored-By Claude -> block",
         "pre_commit_no_ai_trailer",
         {"tool_name": "Bash", "tool_input": {"command": 'git commit -m "feat: x\n\nCo-Authored-By: Claude <noreply@anthropic.com>"'}},
         2),
        ("pre_commit: Generated with Claude Code -> block",
         "pre_commit_no_ai_trailer",
         {"tool_name": "Bash", "tool_input": {"command": 'git commit -m "feat: x\n\n🤖 Generated with Claude Code"'}},
         2),
        ("pre_commit: clean message -> allow",
         "pre_commit_no_ai_trailer",
         {"tool_name": "Bash", "tool_input": {"command": 'git commit -m "feat: clean message"'}},
         0),
        ("pre_commit: non-commit Bash -> allow",
         "pre_commit_no_ai_trailer",
         {"tool_name": "Bash", "tool_input": {"command": 'git status'}},
         0),

        # ---- safe_kill_guard ----
        ("safe_kill: Stop-Process -Name python -> block",
         "safe_kill_guard",
         {"tool_name": "PowerShell", "tool_input": {"command": "Stop-Process -Name python -Force"}},
         2),
        ("safe_kill: Stop-Process -Name pythonw -> block",
         "safe_kill_guard",
         {"tool_name": "PowerShell", "tool_input": {"command": "Stop-Process -Name pythonw -Force"}},
         2),
        ("safe_kill: port-scoped kill on 8446 (protected) -> block",
         "safe_kill_guard",
         {"tool_name": "PowerShell", "tool_input": {"command": "Get-NetTCPConnection -LocalPort 8446 | Select -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }"}},
         2),
        ("safe_kill: port-scoped kill on 8445 (project port) -> allow",
         "safe_kill_guard",
         {"tool_name": "PowerShell", "tool_input": {"command": "Get-NetTCPConnection -LocalPort 8445 | Select -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }"}},
         0),
        ("safe_kill: git push --force origin main -> block",
         "safe_kill_guard",
         {"tool_name": "Bash", "tool_input": {"command": "git push --force origin main"}},
         2),
        ("safe_kill: git push --force feature/x -> allow",
         "safe_kill_guard",
         {"tool_name": "Bash", "tool_input": {"command": "git push --force origin feature/foo"}},
         0),
        ("safe_kill: git commit --no-verify -> block",
         "safe_kill_guard",
         {"tool_name": "Bash", "tool_input": {"command": "git commit --no-verify -m hi"}},
         2),

        # ---- venv_discipline ----
        ("venv: python -m venv venv -> block",
         "venv_discipline",
         {"tool_name": "PowerShell", "cwd": str(REPO), "tool_input": {"command": "python -m venv venv"}},
         2),
        ("venv: python -m venv .venv -> allow",
         "venv_discipline",
         {"tool_name": "PowerShell", "cwd": str(REPO), "tool_input": {"command": "python -m venv .venv"}},
         0),
        ("venv: activate.ps1 -> block",
         "venv_discipline",
         {"tool_name": "PowerShell", "cwd": "E:/automation/app-launcher", "tool_input": {"command": ".\\.venv\\Scripts\\Activate.ps1"}},
         2),
        ("venv: source .venv/bin/activate -> block",
         "venv_discipline",
         {"tool_name": "Bash", "cwd": "E:/automation/app-launcher", "tool_input": {"command": "source .venv/bin/activate"}},
         2),
        ("venv: bare python with .venv present -> block",
         "venv_discipline",
         {"tool_name": "PowerShell", "cwd": "E:/automation/app-launcher", "tool_input": {"command": "python script.py"}},
         2),
        ("venv: path-scoped venv python -> allow",
         "venv_discipline",
         {"tool_name": "PowerShell", "cwd": "E:/automation/app-launcher", "tool_input": {"command": "& .\\.venv\\Scripts\\python.exe -m pip install foo"}},
         0),
        ("venv: bare python with NO .venv -> allow",
         "venv_discipline",
         {"tool_name": "Bash", "cwd": tempfile.gettempdir(), "tool_input": {"command": "python --version"}},
         0),
    ]

    # ---- py_syntax_check needs real files ----
    tmp = Path(tempfile.mkdtemp(prefix="claude-config-test-"))
    broken = tmp / "broken.py"
    good   = tmp / "good.py"
    broken.write_text("def foo(:\n    pass\n", encoding="utf-8")
    good.write_text("def foo():\n    return 1\n", encoding="utf-8")

    cases.append((
        "py_syntax: broken file -> block",
        "py_syntax_check",
        {"tool_name": "Edit", "cwd": str(tmp), "tool_input": {"file_path": str(broken)}},
        2,
    ))
    cases.append((
        "py_syntax: good file -> allow",
        "py_syntax_check",
        {"tool_name": "Edit", "cwd": str(tmp), "tool_input": {"file_path": str(good)}},
        0,
    ))
    cases.append((
        "py_syntax: non-py file -> allow",
        "py_syntax_check",
        {"tool_name": "Edit", "cwd": str(tmp), "tool_input": {"file_path": str(tmp / "x.txt")}},
        0,
    ))

    failures = 0
    for name, hook, payload, expected in cases:
        code, _stdout, stderr = run(hook, payload)
        if not assert_exit(name, expected, code, stderr):
            failures += 1

    # Cleanup
    shutil.rmtree(tmp, ignore_errors=True)

    print()
    print(f"Total: {len(cases)} | Failed: {failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
