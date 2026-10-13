"""Record which targeted checks are required after an apply_patch call."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATE_ROOT = PROJECT_ROOT / ".codex" / "state"


def safe_session_id(value: object) -> str:
    text = str(value or "unknown")
    return re.sub(r"[^A-Za-z0-9_.-]", "_", text)[:120] or "unknown"


try:
    event = json.load(sys.stdin)
except (json.JSONDecodeError, OSError):
    raise SystemExit(0)

tool_input = event.get("tool_input")
if not isinstance(tool_input, dict):
    raise SystemExit(0)

patch = tool_input.get("command")
if not isinstance(patch, str):
    raise SystemExit(0)

paths = re.findall(
    r"^\*\*\* (?:Add|Update|Delete) File:\s*(.+?)\s*$",
    patch,
    flags=re.MULTILINE,
)
if not paths:
    raise SystemExit(0)

categories: set[str] = set()
for raw_path in paths:
    normalized = raw_path.replace("\\", "/").lower()
    if normalized.endswith(".wbt"):
        categories.add("webots_world")
    if "/webots/controllers/" in f"/{normalized}" and normalized.endswith(".py"):
        categories.add("webots_python")
    if normalized.endswith("/platformio.ini") or normalized == "platformio.ini":
        categories.add("platformio")
    if "/src/" in f"/{normalized}" and normalized.endswith(
        (".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp")
    ):
        categories.add("platformio")

if not categories:
    raise SystemExit(0)

STATE_ROOT.mkdir(parents=True, exist_ok=True)
state_path = STATE_ROOT / f"{safe_session_id(event.get('session_id'))}.json"

state: dict[str, object] = {"categories": [], "paths": []}
if state_path.exists():
    try:
        loaded = json.loads(state_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            state.update(loaded)
    except (json.JSONDecodeError, OSError):
        pass

existing_categories = set(state.get("categories", []))
existing_paths = set(state.get("paths", []))
state["categories"] = sorted(existing_categories | categories)
state["paths"] = sorted(existing_paths | set(paths))
state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

