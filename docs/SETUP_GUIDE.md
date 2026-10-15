# RobotArmC3 Setup Guide

This guide takes a new Windows computer from a fresh clone to a working robot-arm simulation. The repository contains two independent simulations and one physical-hardware target:

- **Webots** shows the complete 3D arm (the same 3D-printed design as the real arm, loaded from `webots/meshes/`) and runs a Python controller.
- **Wokwi** simulates the ESP32-C3 circuit and runs the compiled Arduino firmware.
- **PlatformIO `physical`** builds the firmware for the real ESP32-C3-DevKitC-02.

The firmware (`src/main.cpp`) and the Webots controller use the same poses and the same calibration commands, so what you tune in one carries over to the other.

## 1. Install the software

Install:

1. [Visual Studio Code](https://code.visualstudio.com/)
2. [PlatformIO IDE for VS Code](https://platformio.org/install/ide?install=vscode)
3. [Wokwi for VS Code](https://docs.wokwi.com/vscode/getting-started)
4. [Webots R2025a](https://cyberbotics.com/)
5. Git, if the project will be cloned or pushed from the terminal

This project expects Webots at:

```text
C:\Program Files\Webots\msys64\mingw64\bin\webots.exe
```

If Webots is installed elsewhere, update `scripts/start-webots.ps1` and `.vscode/tasks.json`.

## 2. Clone and open the correct folder

Clone the repository, then open the **RobotArmC3 root folder** in VS Code. The folder is correct when it directly contains:

```text
platformio.ini
diagram.json
wokwi.toml
src/
webots/
```

Do not open only `src`, `webots`, or `webots/worlds`.

## 3. Run the 3D arm in Webots

### Recommended: VS Code task

1. In VS Code, select **Terminal → Run Task**.
2. Select **Webots: Open robot arm**.
3. Wait for Webots to load `robot_arm.wbt`.

The task launches the world in real-time mode and clears an invalid inherited `QT_OPENGL` value for that Webots process.

### Alternative: PowerShell launcher

From the repository root:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\start-webots.ps1
```

To open the world paused:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\scripts\start-webots.ps1 -Mode pause
```

### Webots controls

The Webots console displays output; it is not a text-entry terminal. Start **Simulation → Real-time**, click inside the 3D view, then press:

| Key | Action |
| --- | --- |
| `H` | Return to the home pose |
| `T` | Test the four joints |
| `P` | Run the pick-and-place sequence |
| `X` | Stop the current movement |
| `B` `S` `E` `G` | Select base, shoulder, elbow, or gripper |
| `+` / `-` | Jog the selected joint 1° |
| `]` / `[` | Jog the selected joint 5° |
| `C` | Print the current pose, ready to paste into code |
| `?` | Print the control menu |

The simulation clock must be advancing for keyboard input and motion to work. Keys other than `X` are ignored while a movement is running, so wait for it to finish before sending the next command.

At `HOME` the arm looks like an "L": the upper arm is vertical and the forearm is horizontal. That is the real arm's pose at servo 90°.

The arm's parts are STL files in `webots/meshes/` (millimetres, Z up, with the table at height 0). If the CAD model changes, export each part again with the same file name; the world scales them by 0.001 and needs no other change.

## 4. Run the ESP32 circuit in Wokwi

1. Run **PlatformIO: Build**. The default environment is `wokwi`.
2. Confirm the build finishes with `SUCCESS`.
3. Open `diagram.json`.
4. Start **Wokwi: Start Simulator** from the Command Palette.
5. Use the terminal built into the Wokwi window.

Enter `t`, `h`, `p`, `x`, or `?`, followed by Enter. The calibration commands (`b`/`s`/`e`/`g` to select a joint, `+`/`-` and `]`/`[` to jog it, `c` to print the pose) work the same way as in Webots. Wokwi uses the compiled file at `.pio/build/wokwi/firmware.bin`, so rebuild after changing `src/main.cpp`.

Command-line build:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run -e wokwi
```

## 5. Build for the physical ESP32-C3

Build without uploading:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run -e physical
```

Before uploading or powering servos:

- use a regulated external 5 V servo supply;
- connect the external supply ground to ESP32 ground;
- do not power all four servos through the ESP32 5 V pin;
- remove loads or servo horns during initial calibration where practical; and
- test one joint at a time before running the automatic sequence.

The example angle limits are conservative starting points, not guaranteed mechanical limits for every arm.

### Calibrate on the real arm

Open a serial terminal at 115200 baud (the Wokwi terminal uses the same commands):

1. Select one joint with `b`, `s`, `e`, or `g`, then jog it with `+`/`-` (1°) or `]`/`[` (5°). Record the angles at each end where the joint still moves freely.
2. Put the safe limits in the `CONFIG` table in `src/main.cpp`. If a servo turns the wrong way for how it is mounted, set `invert` to `true`; if a horn is a few degrees off, use `trim`.
3. Type `x` at any time to stop a movement. This is a software stop only, so keep a hand near the servo-power switch.
4. Fine-tune the poses with the jog keys and use `c` to print the pose you reached.

The servo pulse range starts at a conservative 1000–2000 µs (`SERVO_MIN_US` and `SERVO_MAX_US` at the top of `src/main.cpp`). After wiring, check it against your servos and change it only if a joint cannot reach its full range; recalibrate the limits afterwards.

### Pick-and-place positions

The poses assume an object on the table about 110 mm in front of the base axis, with the table at the very bottom of the arm base. To plan another position:

```powershell
python tools/arm_poses.py --reach 140 --pick-height 20
```

The tool prints the eight poses and lines to paste into `src/main.cpp` and `webots/controllers/arm_controller/arm_controller.py`. Treat them as a starting point, and test each pose without an object first.

## 6. Common Webots problems

### Webots opens but the 3D view is blank

Check whether Windows contains an invalid value such as:

```text
QT_OPENGL=angle or software
```

The included launcher removes it for Webots automatically. To remove the user-level setting permanently, close Webots and run:

```powershell
[Environment]::SetEnvironmentVariable('QT_OPENGL', $null, 'User')
```

Restart VS Code afterward because existing terminals retain their old environment.

### The arm is not in view

Select **View → Restore Viewpoint**. The repository's world file contains a camera aimed at the arm.

### No Run Simulation button is visible

Use **Simulation → Real-time**. If panels or menus appear missing, use **Tools → Restore Layout** and **Tools → 3D View**. Do not use Fast mode when you need graphical rendering.

### PowerShell waits at a `>>` prompt

A quotation mark is missing. Press `Ctrl+C` and rerun the command. Prefer the included launcher to avoid long quoted paths.

### Keys do not move the arm

Verify the simulation clock is advancing, click the 3D view rather than the console, and press `T`. Keys are ignored while a movement is running (other than `X`), so wait for the arm to stop first.

### The arm or some parts are missing

The world loads its parts from `webots/meshes/*.stl`. Check that all nine files are present in that folder after cloning.

### Webots does not open from a background or hidden shell

Start it from the VS Code task or from a normal PowerShell window. Launching the script from a hidden window can leave no Webots window at all.

See [Troubleshooting](TROUBLESHOOTING.md) for Wokwi, serial, build, and physical-hardware issues.

## 7. Verify before pushing

From the repository root, build both firmware targets:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run -e wokwi -e physical
```

Then open Webots using the VS Code task, click the 3D view, and press `T` (and `P` to run the full sequence). Review the files Git will include:

```powershell
git status
git diff
```

A complete change set for the current version includes:

- `src/main.cpp`, `webots/worlds/robot_arm.wbt`, and `webots/controllers/arm_controller/arm_controller.py`;
- the nine new files in `webots/meshes/` and the new `tools/arm_poses.py`;
- the updated `README.md` and the three guides under `docs/`.

`webots/worlds/.robot_arm.wbproj` only stores the Webots window layout. Commit it only if you want that layout shared; otherwise run `git restore webots/worlds/.robot_arm.wbproj` before committing.

The `.pio` build directory and temporary Codex validation state are ignored.

## 8. Push to GitHub

After reviewing the changes:

```powershell
git add .
git commit -m "Add 3D-printed arm model, jog calibration, and reach-based poses"
git pull --rebase origin main
git push origin main
```

If the rebase reports a conflict, do not force-push. Resolve the marked files, run `git add` for each resolved file, and continue with `git rebase --continue` before pushing.

If this local repository does not have a GitHub remote yet, create an empty repository on GitHub and follow the remote commands GitHub displays. Do not commit passwords, API keys, Wi-Fi credentials, or private serial logs.
