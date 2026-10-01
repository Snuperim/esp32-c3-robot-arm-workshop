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

## Wokwi simulation quick start

### 1. Install the required VS Code extensions

Install:

- **PlatformIO IDE**
- **Wokwi for VS Code**

VS Code should recommend both extensions automatically when this repository is opened. Activate/sign in to the Wokwi extension if prompted.

### 2. Clone and open the repository

Clone or download this repository, then open the **repository root folder** in VS Code.

The folder you open should contain:

```text
platformio.ini
diagram.json
wokwi.toml
src/
```

Do not open only the `src` folder.

### 3. Build the simulation firmware

The default PlatformIO environment is `wokwi`, so the normal **PlatformIO: Build** command builds the simulator firmware.

You can also use:

```text
PlatformIO → Project Tasks → wokwi → Build
```

Wait for:

```text
SUCCESS
```

After a successful build, this file should exist:

```text
.pio/build/wokwi/firmware.bin
```

Wokwi cannot start until the firmware has been built.

### 4. Start Wokwi

Open `diagram.json`, then either:

- press the green **Play** button in the Wokwi diagram view, or
- press `Ctrl+Shift+P` and run **Wokwi: Start Simulator**.

The ESP32-C3 and four virtual servos should appear.

### 5. Use the built-in Wokwi terminal

The Wokwi terminal is the recommended workshop interface. You do **not** need a physical COM port or PlatformIO Serial Monitor for the normal simulation workflow.

You should see:

```text
Robot arm ready!

===========================
 ROBOT ARM CONTROL
===========================
h = HOME
t = Test servos
p = Pick and place
? = Show this menu
===========================
```

Type a command and press Enter:

| Command | Action |
| --- | --- |
| `h` | Move to the home pose |
| `t` | Test each servo and return home |
| `p` | Run the complete pick-and-place sequence |
| `?` | Print the command menu |

Start with `t`.

### 6. Edit and rerun

The main program is `src/main.cpp`.

After changing the code:

1. Stop the Wokwi simulation.
2. Run **PlatformIO: Build** again.
3. Restart Wokwi.

> Wokwi runs the **compiled firmware**, not `main.cpp` directly. If you change the source code without rebuilding, the simulator will still run the previous firmware.

## Optional: PlatformIO Serial Monitor with Wokwi

Wokwi already includes an interactive terminal, so this section is not required for the workshop.

For debugging, the simulation also exposes its UART through RFC2217 on port 4000. Start Wokwi first, then run **PlatformIO: Serial Monitor** using the `wokwi` environment.

The monitor should connect to:

```text
rfc2217://localhost:4000
```

The serial path is configured in three places:

- `wokwi.toml` exposes Wokwi's simulated UART on RFC2217 port 4000.
- the `wokwi` environment in `platformio.ini` points PlatformIO at `rfc2217://localhost:4000`.
- `diagram.json` crosses ESP32 TX/RX with `$serialMonitor` RX/TX.

Do not use the RFC2217 monitor configuration for the physical robot.

## Simulation troubleshooting

### `firmware.bin not found`

Build the `wokwi` environment first and confirm that this exists:

```text
.pio/build/wokwi/firmware.bin
```

### Wokwi runs but the terminal is empty

- Confirm the simulator is actually running rather than paused.
- Type `?` and press Enter.
- If needed, stop and restart the simulator.

### Code changes do not appear

Stop Wokwi, rebuild with PlatformIO, then restart Wokwi.

### Servos do not move

Run `t`. If the terminal prints the test messages but the virtual servos do not move, check `diagram.json` and verify:

```text
GPIO3 → Base
GPIO4 → Shoulder
GPIO5 → Elbow
GPIO6 → Gripper
```

For more detail, see [Troubleshooting](docs/TROUBLESHOOTING.md).

## Physical robot setup

The repository has a separate PlatformIO environment named `physical` for the real ESP32-C3-DevKitC-02 board.

1. Disconnect servo power while checking all signal and ground wiring.
2. Connect each servo signal to the GPIO in the pin map.
3. Connect the ESP32 ground and external servo-supply ground together.
4. Remove servo horns or unload the joints for the first power-on where practical.
5. In PlatformIO, select **Project Tasks → physical → Build/Upload**.
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
| `platformio.ini` | Separate Wokwi and physical-board PlatformIO environments |
| `diagram.json` | Wokwi ESP32-C3 and four-servo circuit |
| `wokwi.toml` | Wokwi firmware paths and optional serial forwarding |
| `docs/WORKSHOP_GUIDE.md` | Suggested facilitator plan and calibration activity |
| `docs/TROUBLESHOOTING.md` | Build, simulation, serial, and hardware fixes |
| `.github/workflows/build.yml` | Automatic PlatformIO builds for pushes and pull requests |

## Reproducible builds

The Espressif platform and ESP32Servo library versions are pinned in `platformio.ini`. GitHub Actions builds both the Wokwi and physical environments on every push and pull request, helping catch dependency or compilation problems before a workshop.
