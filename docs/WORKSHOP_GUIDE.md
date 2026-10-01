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
- pre-manufactured robot-arm parts and hardware;
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

Begin near 90°. Move in small increments and record the mechanical range where the joint moves freely. Leave a safety margin at both ends, then update the corresponding minimum and maximum constants in `src/main.cpp`.

The existing `t` command uses moderate test positions. Change those test positions if the physical mechanism cannot safely reach them.

### 6. Calibrate poses

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

- Replace linear interpolation with eased motion.
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
