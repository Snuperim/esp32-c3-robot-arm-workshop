# RobotArmC3 Setup Guide

This guide takes a new Windows computer from a fresh clone to a working robot-arm simulation. The repository contains two independent simulations and one physical-hardware target:

- **Webots** shows the complete 3D arm and runs a Python controller.
- **Wokwi** simulates the ESP32-C3 circuit and runs the compiled Arduino firmware.
- **PlatformIO `physical`** builds the firmware for the real ESP32-C3-DevKitC-02.

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
| `?` | Print the control menu |

The simulation clock must be advancing for keyboard input and motion to work.

## 4. Run the ESP32 circuit in Wokwi

1. Run **PlatformIO: Build**. The default environment is `wokwi`.
2. Confirm the build finishes with `SUCCESS`.
3. Open `diagram.json`.
4. Start **Wokwi: Start Simulator** from the Command Palette.
5. Use the terminal built into the Wokwi window.

Enter `t`, `h`, `p`, or `?`, followed by Enter. Wokwi uses the compiled file at `.pio/build/wokwi/firmware.bin`, so rebuild after changing `src/main.cpp`.

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

Verify the simulation clock is advancing, click the 3D view rather than the console, and press `T`.

See [Troubleshooting](TROUBLESHOOTING.md) for Wokwi, serial, build, and physical-hardware issues.

## 7. Verify before pushing

From the repository root, build both firmware targets:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run -e wokwi -e physical
```

Then open Webots using the VS Code task and press `T`. Review the files Git will include:

```powershell
git status
git diff
```

The `.pio` build directory and temporary Codex validation state are ignored.

## 8. Push to GitHub

After reviewing the changes:

```powershell
git add .
git commit -m "Add Webots simulation and setup guide"
git pull --rebase origin main
git push origin main
```

If the rebase reports a conflict, do not force-push. Resolve the marked files, run `git add` for each resolved file, and continue with `git rebase --continue` before pushing.

If this local repository does not have a GitHub remote yet, create an empty repository on GitHub and follow the remote commands GitHub displays. Do not commit passwords, API keys, Wi-Fi credentials, or private serial logs.
