#!/usr/bin/env python3
import json
import sys
import re
from pathlib import Path


def main():
    try:
        input_data = json.load(sys.stdin)
        command = input_data.get("command", "")
        if not command:
            print(json.dumps({"permission": "allow"}))
            sys.exit(0)

        # Patterns to block: direct use of these tools (not if run via uv)
        patterns = {
            r"(^|&&|\s)(pip\s+)": "uv ",
            r"(^|&&|\s)(pipenv\s+)": "uv ",
            r"(^|&&|\s)(poetry\s+)": "uv ",
            r"(^|&&|\s)(python3?\b)": "uv run ",
        }

        # Do not block if already using uv run
        if re.search(r"\buv\s+run\b", command):
            print(json.dumps({"permission": "allow"}))
            sys.exit(0)

        blocked = None
        suggestion = None

        for pattern, replacement in patterns.items():
            if re.search(pattern, command):
                blocked = command
                suggestion = re.sub(pattern, f" {replacement}", command)
                break

        if blocked:
            log_file = Path(__file__).parent.parent / "uv_enforcement.json"
            entry = {"blocked_command": blocked, "suggested_command": suggestion}
            logs = json.loads(log_file.read_text()) if log_file.exists() else []
            logs.append(entry)
            log_file.write_text(json.dumps(logs, indent=2))

            print(
                json.dumps(
                    {
                        "permission": "deny",
                        "userMessage": (
                            f"Use `uv` instead of `{blocked.split()[0]}`.\n"
                            f"Suggested: `{suggestion.strip()}`"
                        ),
                    }
                )
            )
        else:
            print(json.dumps({"permission": "allow"}))

        sys.exit(0)

    except Exception as e:
        print(json.dumps({"permission": "allow", "agentMessage": f"hook error: {e}"}))
        sys.exit(0)


if __name__ == "__main__":
    main()

