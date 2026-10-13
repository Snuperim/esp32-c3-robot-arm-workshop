"""Run queued RobotArmC3 checks once, just before Codex finishes a turn."""

from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATE_ROOT = PROJECT_ROOT / ".codex" / "state"


def first_existing_path(*candidates: Path | None) -> Path | None:
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate
    return None


user_profile = Path(os.environ.get("USERPROFILE", Path.home()))
program_files = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
webots_home = os.environ.get("WEBOTS_HOME")

WEBOTS = first_existing_path(
    Path(webots_home) / "msys64" / "mingw64" / "bin" / "webots.exe"
    if webots_home
    else None,
    program_files / "Webots" / "msys64" / "mingw64" / "bin" / "webots.exe",
    Path(shutil.which("webots") or "") if shutil.which("webots") else None,
)
PLATFORMIO = first_existing_path(
    user_profile / ".platformio" / "penv" / "Scripts" / "platformio.exe",
    Path(shutil.which("platformio") or "") if shutil.which("platformio") else None,
    Path(shutil.which("pio") or "") if shutil.which("pio") else None,
)


def safe_session_id(value: object) -> str:
    text = str(value or "unknown")
    return re.sub(r"[^A-Za-z0-9_.-]", "_", text)[:120] or "unknown"


def decode_output(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return str(value)


def emit_continue(system_message: str | None = None) -> None:
    payload: dict[str, object] = {"continue": True}
    if system_message:
        payload["systemMessage"] = system_message
    print(json.dumps(payload))


def check_python_controller() -> tuple[bool, str]:
    controller_root = PROJECT_ROOT / "webots" / "controllers"
    failures: list[str] = []
    for path in controller_root.rglob("*.py"):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError) as exc:
            failures.append(f"{path.relative_to(PROJECT_ROOT)}: {exc}")
    if failures:
        return False, "Python controller syntax failed:\n" + "\n".join(failures)
    return True, "Webots Python controller syntax passed."


def check_platformio() -> tuple[bool, str]:
    if PLATFORMIO is None:
        return False, "PlatformIO executable was not found."
    try:
        result = subprocess.run(
            [str(PLATFORMIO), "run", "-e", "wokwi", "-e", "physical"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"PlatformIO validation could not complete: {exc}"
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        return False, "PlatformIO build failed:\n" + output[-5000:]
    return True, "PlatformIO wokwi and physical builds passed."


def check_webots_world() -> tuple[bool, str]:
    world = PROJECT_ROOT / "webots" / "worlds" / "robot_arm.wbt"
    if WEBOTS is None:
        return False, "Webots executable was not found."
    if not world.exists():
        return False, f"Webots world not found: {world}"

    environment = os.environ.copy()
    environment.pop("QT_OPENGL", None)
    port = 12000 + (os.getpid() % 20000)
    command = [
        str(WEBOTS),
        "--batch",
        "--no-rendering",
        "--stdout",
        "--stderr",
        "--mode=fast",
        f"--port={port}",
        str(world),
    ]

    output = ""
    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        output = (result.stdout or "") + (result.stderr or "")
    except subprocess.TimeoutExpired as exc:
        output = decode_output(exc.stdout) + decode_output(exc.stderr)
    except OSError as exc:
        return False, f"Webots validation could not start: {exc}"

    blocking_markers = ("ERROR:", "Failed to load due to syntax error")
    if any(marker in output for marker in blocking_markers):
        return False, "Webots validation failed:\n" + output[-5000:]
    if "Starting controller" not in output and "WEBOTS ROBOT ARM CONTROL" not in output:
        return False, "Webots did not reach controller startup within 20 seconds:\n" + output[-5000:]
    return True, "Webots world parsed and the arm controller started."


try:
    event = json.load(sys.stdin)
except (json.JSONDecodeError, OSError):
    emit_continue("RobotArmC3 stop hook received invalid event data.")
    raise SystemExit(0)

state_path = STATE_ROOT / f"{safe_session_id(event.get('session_id'))}.json"
if not state_path.exists():
    emit_continue()
    raise SystemExit(0)

try:
    state = json.loads(state_path.read_text(encoding="utf-8"))
except (json.JSONDecodeError, OSError) as exc:
    emit_continue(f"Could not read RobotArmC3 validation state: {exc}")
    raise SystemExit(0)

categories = set(state.get("categories", []))
checks: list[tuple[bool, str]] = []
if "webots_python" in categories:
    checks.append(check_python_controller())
if "webots_world" in categories:
    checks.append(check_webots_world())
if "platformio" in categories:
    checks.append(check_platformio())

failures = [message for passed, message in checks if not passed]
successes = [message for passed, message in checks if passed]

if not failures:
    state_path.unlink(missing_ok=True)
    emit_continue(" ".join(successes) if successes else None)
    raise SystemExit(0)

failure_text = "\n\n".join(failures)
if event.get("stop_hook_active"):
    state_path.unlink(missing_ok=True)
    emit_continue(
        "RobotArmC3 validation is still failing after one automatic repair pass:\n"
        + failure_text
    )
    raise SystemExit(0)

print(
    json.dumps(
        {
            "decision": "block",
            "reason": (
                "Fix the following RobotArmC3 validation failure, then rerun the "
                "affected check before finishing:\n" + failure_text
            ),
        }
    )
)
