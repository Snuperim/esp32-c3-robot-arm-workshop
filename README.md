# ESP32-C3 Robot Arm Workshop

An Arduino/PlatformIO project for teaching how to control a four-servo robot arm with an ESP32-C3. The project can run in Wokwi before participants connect real hardware.

The arm supports a home position, an individual servo test, and a complete pick-and-place sequence. Commands are sent through a 115200-baud serial terminal.

> **Hardware safety:** Do not power four servos from the ESP32 board's 5 V pin on a physical robot. Use a regulated external 5 V supply sized for the combined stall current, and connect the supply ground to ESP32 ground. Calibrate every joint before running the automatic sequence.

## Hardware and pin map

| Joint | ESP32-C3 GPIO | Starting safe range |
| --- | ---: | ---: |
| Base | 3 | 20–160° |
| Shoulder | 4 | 30–150° |
| Elbow | 5 | 30–150° |
| Gripper | 6 | 20–90° |

The ranges are conservative starting values. Mechanical limits vary between robot arms and must be measured on the real assembly.

## Simulation quick start

Install these VS Code extensions:

- PlatformIO IDE
- Wokwi for VS Code

Then:

1. Clone or download this repository and open its root folder in VS Code.
2. Run **PlatformIO: Build**.
3. Open `diagram.json` and run **Wokwi: Start Simulator**.
4. Keep the Wokwi simulator tab visible so the simulation continues running.
5. Open PlatformIO Serial Monitor after Wokwi starts.
6. If you want to see the boot messages, restart the simulation while the monitor is connected.
7. Type `t` and press Enter to test the four servos.

The built-in Wokwi terminal can also send the same commands.

## Commands

| Command | Action |
| --- | --- |
| `h` | Move to the home pose |
| `t` | Test each servo and return home |
| `p` | Run the complete pick-and-place sequence |
| `?` | Print the command menu |

Commands are case-insensitive except for `?`.

## Serial connection used by the simulator

```mermaid
flowchart LR
    A[PlatformIO Serial Monitor] <-->|RFC2217 port 4000| B[Wokwi serial monitor]
    B <-->|TX and RX| C[ESP32-C3 UART0]
```

Three settings make this work:

- `wokwi.toml` exposes Wokwi's simulated UART on RFC2217 port 4000.
- `platformio.ini` tells PlatformIO to use `rfc2217://localhost:4000`.
- `diagram.json` explicitly crosses ESP32 TX/RX with `$serialMonitor` RX/TX.

See [Troubleshooting](docs/TROUBLESHOOTING.md) if the monitor connects but shows no firmware output.

## Physical robot setup

1. Disconnect servo power while checking all signal and ground wiring.
2. Connect each servo signal to the GPIO in the pin map.
3. Connect the ESP32 ground and external servo-supply ground together.
4. Remove servo horns or unload the joints for the first power-on where practical.
5. Build and upload the firmware with PlatformIO.
6. Run `t` and verify one joint at a time.
7. Adjust the limits and poses in `src/main.cpp` before running `p`.

Never force a stalled servo. Disconnect power if a joint reaches a mechanical stop, vibrates continuously, or becomes hot.

## How the firmware works

Each arm position is a `Pose` containing base, shoulder, elbow, and gripper angles. `constrainPose()` clamps every target to its configured limits. `moveTo()` linearly interpolates all four joints over 50 steps, producing coordinated motion. The predefined poses form the pick-and-place sequence.

The movement code uses blocking delays to keep it approachable for a workshop. Serial commands are processed after the current movement finishes.

## Repository layout

| Path | Purpose |
| --- | --- |
| `src/main.cpp` | Robot poses, servo control, motion, and serial commands |
| `platformio.ini` | Board, dependency, and PlatformIO monitor configuration |
| `diagram.json` | Wokwi ESP32-C3 and four-servo circuit |
| `wokwi.toml` | Wokwi firmware paths and serial forwarding |
| `docs/WORKSHOP_GUIDE.md` | Suggested facilitator plan and calibration activity |
| `docs/TROUBLESHOOTING.md` | Build, simulation, serial, and hardware fixes |
| `.github/workflows/build.yml` | Automatic PlatformIO build for pushes and pull requests |

## Reproducible builds

The Espressif platform and ESP32Servo library versions are pinned in `platformio.ini`. GitHub Actions builds the firmware on every push and pull request, helping catch dependency or compilation problems before a workshop.
