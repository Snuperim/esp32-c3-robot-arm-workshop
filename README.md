# ESP32-C3 Robot Arm Workshop

An Arduino/PlatformIO workshop project for controlling a four-servo robot arm with an ESP32-C3. It includes a complete 3D arm in Webots, an ESP32 circuit simulation in Wokwi, and a separate firmware target for the physical robot.

The arm currently supports a home position, an individual servo test, and a complete pick-and-place sequence. Commands to the servos are sent through a 115200-baud serial terminal.

## Start here

For installation, Webots controls, Wokwi setup, physical-arm safety, troubleshooting, and GitHub push commands, follow the **[complete setup guide](docs/SETUP_GUIDE.md)**.

### Webots 3D simulation

In VS Code, select **Terminal → Run Task → Webots: Open robot arm**. The included launcher opens the correct world in real-time mode and avoids the invalid `QT_OPENGL` setting that can cause a blank viewport.

Click inside the Webots 3D view and press:

| Key | Action |
| --- | --- |
| `H` | Return home |
| `T` | Test every joint |
| `P` | Run pick-and-place |
| `X` | Stop the current movement |
| `B` `S` `E` `G` | Select base, shoulder, elbow, or gripper |
| `+` / `-` | Jog the selected joint 1° |
| `]` / `[` | Jog the selected joint 5° |
| `C` | Print the current pose, ready to paste into code |
| `?` | Print the control menu |

The Webots console is output-only. Keyboard commands are received by the 3D view while the simulation is running.

The arm in Webots is the same 3D-printed design as the real arm. Its meshes are exported from CAD into `webots/meshes/` (millimetres, Z up, the table at height 0).

### Wokwi circuit simulation

Run **PlatformIO: Build**, open `diagram.json`, and start **Wokwi: Start Simulator**. Type `h`, `t`, `p`, `x`, or `?` into Wokwi's built-in terminal and press Enter. The calibration commands (`b`/`s`/`e`/`g`, `+`/`-`, `]`/`[`, `c`) work the same way as in Webots.

> **Hardware safety:** Do not power four servos from the ESP32 board's 5 V pin on a physical robot. Use a regulated external 5 V supply sized for the combined stall current, and connect the supply ground to the ESP32 ground. Calibrate every joint before running the automatic sequence.

## Hardware and pin map

| Joint | ESP32-C3 GPIO | Starting safe range |
| --- | ---: | ---: |
| Base | 3 | 20–160° |
| Shoulder | 4 | 30–150° |
| Elbow | 5 | 30–150° |
| Gripper | 6 | 20–90° |

The ranges are conservative starting values and are dependent on the individual hardware. Mechanical limits vary between robot arms and must be measured on the real assembly and updated + tested in this simulation.

## Wokwi simulation quick start guide

### 1. Install the required VS Code extensions

Install:

- **PlatformIO IDE**
- **Wokwi for VS Code**

VS Code should recommend both extensions automatically when this repository is opened. Activate/sign in to the Wokwi extension in a browser if prompted.

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

The Wokwi terminal is the recommended interface for workshops. You do **not** need a physical COM port or PlatformIO Serial Monitor for the normal simulation workflow.

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

### `firmware.bin not found.`

Build the `wokwi` environment first and confirm that this exists:

```text
.pio/build/wokwi/firmware.bin
```

### Wokwi runs, but the terminal is empty

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
6. Select one joint (`b`, `s`, `e`, or `g`) and jog it with `+`/`-` in small steps. Record the range where it moves freely.
7. Put those limits in the `CONFIG` table in `src/main.cpp`. If a servo turns the wrong way, set its `invert` flag; if a horn is slightly off, use `trim`.
8. Run `t`, then check the poses one at a time before running `p`. Type `x` at any time to stop a movement.

Never force a stalled servo. Disconnect power if a joint reaches a mechanical stop, vibrates continuously, or becomes hot.

The servo pulse range (`SERVO_MIN_US` / `SERVO_MAX_US`) starts at a conservative 1000–2000 µs. Check it against your servos after wiring and change it only if a joint cannot reach its full range.

## How the firmware works

Each arm position is a `Pose` containing base, shoulder, elbow, and gripper angles. `CONFIG` holds each joint's pin, safe range, direction, and trim. `constrainPose()` clamps every target to its range. `moveTo()` linearly interpolates all four joints over 50 steps, producing coordinated motion, and the predefined poses form the pick-and-place sequence.

The movement code uses blocking delays to keep it approachable for a workshop. Typing `x` is checked during a movement and stops it; other keys typed during a movement are ignored.

## Pick-and-place poses

The poses are worked out for an object on the table about 110 mm in front of the base axis, with the table at the very bottom of the arm base (height 0). The shoulder axis is 87.5 mm above the table, so the arm has to lean well forward to reach it: at the pick position the shoulder is near 132° and the elbow near 124°.

The end effector is one servo with two straight jaws, like tweezers: a fixed jaw on the forearm and a moving jaw on the servo horn, driven 1:1. At gripper angle 90° the jaws touch and a smaller angle opens the moving jaw (40° is about 50° open, wide enough for a 25 mm object). The `GRAB` angle of 58° closes on a 25 mm object, so tune it for your own.

To plan a different position, run:

```powershell
python tools/arm_poses.py --reach 140 --pick-height 20
```

It prints the eight poses and ready-to-paste lines for `src/main.cpp` and `arm_controller.py`. Treat the result as a starting point and tune it on the real arm.

## Repository layout

| Path | Purpose |
| --- | --- |
| `src/main.cpp` | Robot poses, servo control, motion, and serial commands |
| `platformio.ini` | Separate Wokwi and physical-board PlatformIO environments |
| `diagram.json` | Wokwi ESP32-C3 and four-servo circuit |
| `wokwi.toml` | Wokwi firmware paths and optional serial forwarding |
| `webots/worlds/robot_arm.wbt` | Complete 3D robot-arm world |
| `webots/meshes/*.stl` | Arm parts exported from CAD (mm, Z up), used by the world |
| `webots/controllers/arm_controller/arm_controller.py` | Webots keyboard and motion controller |
| `tools/arm_poses.py` | Works out servo angles for pick and place positions |
| `scripts/start-webots.ps1` | Reliable Windows Webots launcher |
| `docs/SETUP_GUIDE.md` | Complete installation, simulation, and GitHub guide |
| `docs/WORKSHOP_GUIDE.md` | Suggested facilitator plan and calibration activity |
| `docs/TROUBLESHOOTING.md` | Build, simulation, serial, and hardware fixes |
| `.github/workflows/build.yml` | Automatic PlatformIO builds for pushes and pull requests |

## Reproducible builds

The Espressif platform and ESP32Servo library versions are pinned in `platformio.ini`. GitHub Actions builds both the Wokwi and physical environments on every push and pull request, helping catch dependency or compilation problems before a workshop.
