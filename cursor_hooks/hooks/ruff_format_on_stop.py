#!/usr/bin/env python3
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import os

DEBUG_LOG = Path("/tmp/uv_ruff_hook_debug.log")
DEBUG_ENABLED = False  # Set to True to enable debug logging

uv_path = os.path.expanduser("~/.local/bin/uv")


def log_debug(message: str):
    if DEBUG_ENABLED:
        with DEBUG_LOG.open("a") as f:
            f.write(f"[DEBUG] {datetime.now().isoformat()} {message}\n")


def run_command(cmd, cwd=None, timeout=60):
    """Run subprocess safely and log output."""
    log_debug(f"Running command: {' '.join(cmd)} (cwd={cwd})")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        log_debug(f"Exit {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        log_debug(f"Command failed: {e}")
        return 1, "", str(e)


def is_git_repo(path: Path) -> bool:
    code, _, _ = run_command(["git", "rev-parse", "--git-dir"], cwd=path)
    return code == 0


def get_modified_files(workspace: Path):
    if is_git_repo(workspace):
        code, out, _ = run_command(["git", "diff", "--name-only", "HEAD"], cwd=workspace)
        if code != 0:
            return []
        files = [
            workspace / line for line in out.splitlines()
            if line.endswith(".py") and (workspace / line).exists()
        ]
    else:
        cutoff = datetime.now().timestamp() - 600
        files = [
            f for f in workspace.rglob("*.py")
            if f.stat().st_mtime > cutoff
        ]
    log_debug(f"Modified files: {files}")
    return list(set(files))


def uv_ruff_command(args, cwd: Path):
    """Run ruff command using uv."""
    return run_command([uv_path, "run", "ruff"] + args, cwd=cwd)


def main():
    try:
        log_debug("===== Hook started =====")
        input_data = json.load(sys.stdin)
        workspace_roots = input_data.get("workspace_roots", [])
        log_debug(f"Input: {input_data}")

        if not workspace_roots:
            print(json.dumps({}))
            return

        modified_files = []
        for ws in workspace_roots:
            ws_path = Path(ws)
            if ws_path.exists():
                modified_files.extend(get_modified_files(ws_path))

        modified_files = list(set(modified_files))
        if not modified_files:
            log_debug("No modified files found.")
            print(json.dumps({}))
            return

        workspace = Path(workspace_roots[0])

        format_code, format_out, format_err = uv_ruff_command(
            ["format"] + [str(f) for f in modified_files],
            cwd=workspace,
        )

        check_code, check_out, check_err = uv_ruff_command(
            ["check", "--fix"] + [str(f) for f in modified_files],
            cwd=workspace,
        )

        log_debug(f"Format result: {format_code}, err: {format_err}")
        log_debug(f"Check result: {check_code}, err: {check_err}")

        fixes_count = check_out.count("Fixed")
        msg = f"Ruff: formatted {len(modified_files)} file{'s' if len(modified_files)!=1 else ''}"
        if fixes_count:
            msg += f" and applied {fixes_count} fix{'es' if fixes_count!=1 else ''}"

        print(json.dumps({"userMessage": msg}))
        log_debug("===== Hook completed successfully =====")
    except Exception as e:
        log_debug(f"Exception: {e}")
        print(json.dumps({"agentMessage": f"ruff_format_on_stop hook error: {e}"}))


if __name__ == "__main__":
    main()
