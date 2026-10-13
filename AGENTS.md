# RobotArmC3 working instructions

## Autonomy

- Inspect and edit files in this repository without asking first.
- Make reasonable implementation assumptions and complete work end to end.
- Run local builds, syntax checks, and headless simulations automatically.
- Fix failures caused by the requested change and rerun the affected checks.
- Preserve unrelated user changes in the working tree.

## Required verification

- After changing `src/` or `platformio.ini`, build both the `wokwi` and
  `physical` PlatformIO environments. Building does not authorize uploading.
- After changing a Webots `.wbt` file, run Webots in batch/no-rendering mode
  and check for parser or controller-startup errors.
- After changing a Webots Python controller, validate its Python syntax.
- Report non-blocking warnings separately from errors.

## Hardware and repository boundaries

- Never upload firmware to a physical board unless explicitly requested.
- Never activate or move the physical arm unless explicitly requested.
- Do not increase servo limits or physical torque assumptions without
  reporting the change.
- Do not delete project files or run destructive Git commands.
- Do not commit, push, or publish unless explicitly requested.

## Completion

A task is complete when the requested change works, relevant checks pass, and
the final response identifies changed files and verification performed.
