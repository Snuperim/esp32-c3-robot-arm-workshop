# Robot Arm Workshop Guide

This guide is designed for the **3-hour Build Your First Robot Arm workshop**. Participants should have basic CAD familiarity, but they do not need prior robotics, electronics, or embedded-programming experience.

## Learning goals

By the end of the workshop, participants should be able to:

- identify servo power, ground, and signal connections;
- explain why the physical servos require an external power supply;
- understand the relationship between links, joints, actuators, and robot poses;
- use Wokwi to test ESP32-C3 servo-control code before touching hardware;
- control individual joints using angles;
- calibrate conservative software limits; and
- combine poses into a pick-and-place sequence.

## Materials per group

- one ESP32-C3 development board;
- one four-servo robot arm;
- one regulated 5 V servo supply with adequate current capacity;
- USB cable for the ESP32-C3;
- jumper wires and a shared-ground connection;
- the 3D-printed arm parts (base plate, turntable, upper-arm and forearm housings, finger) and the four MG996R servos with their horns and fasteners;
- one lightweight object for the pick-and-place activity; and
- a computer with VS Code, PlatformIO IDE, Wokwi, and the required CAD software installed.

## Preparation before the session

1. Clone this repository on every workshop computer.
2. Run **PlatformIO: Build** and confirm the `wokwi` environment builds successfully.
3. Start Wokwi and confirm that `t` moves all four simulated servos using the **built-in Wokwi terminal**.
4. Check every physical arm for loose fasteners and binding joints.
5. Label the base, shoulder, elbow, and gripper leads.
6. Verify each external power supply and common-ground connection.
7. Mark a safe physical pickup area and drop area.
8. Keep one fully assembled reference arm ready for demonstrations and troubleshooting.

Do not distribute arms with unverified automatic poses. The values in the repository are starting points for simulation and calibration.

## Suggested 3-hour session plan

| Time | Activity |
| ---: | --- |
| 10 min | Demonstrate the finished arm and final pick-and-place challenge |
| 15 min | Introduce links, joints, actuators, DOF, workspace, and servo basics |
| 25 min | CAD activity: inspect or modify links and servo interfaces |
| 20 min | Assemble the pre-manufactured arm and check mechanical clearances |
| 10 min | Break / facilitator inspection |
| 20 min | Build and run the Wokwi simulation using the built-in terminal |
| 15 min | Explore GPIO assignments, `Pose`, and basic servo commands |
| 15 min | Wire the physical arm with external servo power and common ground |
| 20 min | Calibrate one joint at a time and record safe limits |
| 20 min | Tune HOME/PICK/PLACE poses and build the motion sequence |
| 15 min | Pick-and-place challenge and debugging |
| 10 min | Wrap-up, reflection, and extension ideas |

## Participant workflow

### 1. Build the Wokwi firmware

Open the repository root and run **PlatformIO: Build**. The default environment is `wokwi`.

Confirm:

```text
.pio/build/wokwi/firmware.bin
```

exists before starting the simulator.

### 2. Test in Wokwi

Open `diagram.json` and start Wokwi. Use the **terminal built into the Wokwi simulator**; participants do not need PlatformIO Serial Monitor for the normal workshop flow.

Use `?` to show the command menu and `t` to verify all four simulated servos.

### 3. Inspect the pin map

Match GPIO 3, 4, 5, and 6 with the base, shoulder, elbow, and gripper. Ask participants to trace each signal in `diagram.json` before handling the physical wiring.

### 4. Connect physical power safely

Keep servo power disconnected until all wires have been checked. Connect the external supply ground to ESP32 ground. Power the ESP32 by USB and the servos from the external 5 V supply.

Use the `physical` PlatformIO environment when uploading to the real ESP32-C3.

### 5. Calibrate one joint at a time

Start at `HOME` (all joints at 90°). Select one joint with `b`, `s`, `e`, or `g`, then jog it with `+`/`-` (1°) or `]`/`[` (5°). Move in small increments and record the angle at each end where the joint still moves freely. Leave a safety margin at both ends, then enter the values in the `CONFIG` table in `src/main.cpp`.

Two other values live in the same table. If a servo turns the wrong way for how it is mounted, set `invert` to `true`. If a horn was fitted a few degrees off, use `trim` rather than editing every pose.

Type `x` at any time to stop a movement. The `t` command moves each joint ±20° (±40° for the gripper) around its current position and honours the limits.

The servo pulse range (`SERVO_MIN_US` / `SERVO_MAX_US`) starts at a conservative 1000–2000 µs. Check it against your servos after wiring and change it only if a joint cannot reach its full range; recalibrate the limits afterwards.

### 6. Calibrate poses

The poses are worked out for an object on the table about 110 mm in front of the base axis (the table is the bottom of the arm base). To plan another position, use `python tools/arm_poses.py --reach <mm> --pick-height <mm>` and paste the output into `src/main.cpp` (and `arm_controller.py` for Webots). Treat the output as a starting point and fine-tune each pose with the jog keys, using `c` to print the pose you reach.

Adjust poses in this order:

1. `HOME`
2. `PICK_APPROACH`
3. `PICK`
4. `GRAB`
5. `LIFT`
6. `PLACE_APPROACH`
7. `PLACE`
8. `RELEASE`

Test each new pose without an object before running the full sequence. Keep a hand near the servo-power switch during initial tests.

## Discussion and extension ideas

- Turn on `EASED_MOTION` in `src/main.cpp` and compare it with linear interpolation.
- Add potentiometers or a joystick for manual control.
- Store calibrated limits in nonvolatile memory.
- Add a physical emergency-stop input.
- Replace blocking delays with a state machine.
- Add inverse kinematics after participants understand joint-space poses.

## End-of-session checklist

- Return the arm to `HOME`.
- Disconnect servo power before changing wiring.
- Record the calibrated limits for each physical arm.
- Commit working pose changes on a separate branch or per-arm configuration.
- Check that both PlatformIO environments still build before sharing changes.
