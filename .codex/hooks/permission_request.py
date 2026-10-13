"""Conservative approval policy for RobotArmC3 shell commands."""

from __future__ import annotations

import json
import re
import sys


def emit_decision(behavior: str, message: str | None = None) -> None:
    decision: dict[str, str] = {"behavior": behavior}
    if message:
        decision["message"] = message
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PermissionRequest",
                    "decision": decision,
                }
            }
        )
    )


try:
    event = json.load(sys.stdin)
except (json.JSONDecodeError, OSError):
    raise SystemExit(0)

if event.get("tool_name") != "Bash":
    raise SystemExit(0)

tool_input = event.get("tool_input")
if not isinstance(tool_input, dict):
    raise SystemExit(0)

command = tool_input.get("command")
if not isinstance(command, str) or not command.strip():
    raise SystemExit(0)

normalized = command.strip()
lowered = normalized.lower()

# These operations are outside this project's standing authorization.
blocked_patterns = (
    r"\bgit\s+reset\s+--hard\b",
    r"\bgit\s+clean\s+-[^\s]*f",
    r"\b(?:rm|rmdir|del)\b[^\r\n]*(?:/s|-r|-rf)",
    r"\bremove-item\b[^\r\n]*(?:-recurse|-force)",
)
if any(re.search(pattern, lowered) for pattern in blocked_patterns):
    emit_decision("deny", "Destructive repository operation blocked by RobotArmC3 policy.")
    raise SystemExit(0)

# Uploading or commanding hardware must keep the normal human approval path.
hardware_patterns = (
    r"\b(?:pio|platformio)(?:\.exe)?\s+run\b[^\r\n]*(?:^|\s)(?:-t|--target)(?:\s|=|$)",
    r"\besptool(?:\.py|\.exe)?\b",
    r"\bserial_for_url\b",
)
if any(re.search(pattern, lowered) for pattern in hardware_patterns):
    raise SystemExit(0)

# Never auto-approve a compound shell expression from a prefix match.
if any(marker in normalized for marker in (";", "&&", "||", "|", ">", "<", "`", "$(")):
    raise SystemExit(0)

safe_patterns = (
    r"^rg(?:\.exe)?\b",
    r"^git\s+(?:status|diff|log|show|rev-parse)\b",
    r"^(?:pio|platformio)(?:\.exe)?\s+run\b",
    r"^get-(?:content|item|childitem)\b",
    r"^test-path\b",
    r"^python(?:\.exe)?\s+-m\s+(?:py_compile|compileall)\b",
    r"^&?\s*[\"']?c:[/\\]program files[/\\]webots[/\\].*webots\.exe[\"']?\s+--batch\s+--no-rendering\b",
)

if any(re.search(pattern, normalized, flags=re.IGNORECASE) for pattern in safe_patterns):
    emit_decision("allow")
