# Robot Arm Workshop Guide

This guide is designed for a 60–90 minute introductory session. Participants should know basic Arduino concepts but do not need prior robotics experience.

## Learning goals

By the end of the workshop, participants should be able to:

- identify servo power, ground, and signal connections;
- explain why servos require an external power supply;
- control individual joints using angles;
- describe a robot pose as a set of joint angles;
- calibrate conservative software limits; and
- combine poses into a pick-and-place sequence.

## Materials per group

- one ESP32-C3 development board;
- one four-servo robot arm;
- one regulated 5 V servo supply with adequate current capacity;
- USB cable for the ESP32-C3;
- jumper wires and a shared-ground connection;
- one lightweight object for the pick-and-place activity; and
- a computer with VS Code, PlatformIO IDE, and Wokwi installed.

## Preparation before the session

1. Build the repository on every workshop computer.
2. Start Wokwi and confirm that `t` moves all four simulated servos.
3. Check every physical arm for loose fasteners and binding joints.
4. Label the base, shoulder, elbow, and gripper leads.
5. Verify each external power supply and common-ground connection.
6. Mark a safe physical pickup area and drop area.

Do not distribute arms with unverified automatic poses. The values in the repository are starting points for simulation and calibration.

## Suggested session plan

| Time | Activity |
| ---: | --- |
| 10 min | Introduce the ESP32-C3, servo PWM, and safe power wiring |
| 15 min | Build and run the Wokwi simulation |
| 10 min | Explore the `Pose` structure and predefined positions |
| 20 min | Wire the physical arm and test one joint at a time |
| 20 min | Calibrate limits and pick/place poses |
| 10 min | Run the sequence and discuss improvements |

## Participant workflow

### 1. Test in Wokwi

Build the project, start the Wokwi simulator, and open the serial terminal. Use `?` to show the command menu and `t` to verify all four simulated servos.

### 2. Inspect the pin map

Match GPIO 3, 4, 5, and 6 with the base, shoulder, elbow, and gripper. Ask participants to trace each signal in `diagram.json` before handling the physical wiring.

### 3. Connect physical power safely

Keep servo power disconnected until all wires have been checked. Connect the external supply ground to ESP32 ground. Power the ESP32 by USB and the servos from the external 5 V supply.

### 4. Calibrate one joint at a time

Begin near 90°. Move in small increments and record the mechanical range where the joint moves freely. Leave a safety margin at both ends, then update the corresponding minimum and maximum constants in `src/main.cpp`.

The existing `t` command uses moderate test positions. Change those test positions if the physical mechanism cannot safely reach them.

### 5. Calibrate poses

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
- Check that the repository still builds before sharing changes.
