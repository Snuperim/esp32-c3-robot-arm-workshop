# Robot Arm Workshop Guide

This is a follow-along guide for building, wiring, programming and calibrating a four-joint robot arm driven by an ESP32-C3. You do not need earlier robotics or electronics experience. Basic CAD familiarity helps for Chapter 2.

Every chapter has the same three parts:

- **Explain** covers the idea behind the step, so you know why you are doing it.
- **Do** is a short list of steps. Each one ends with what you should see. If you do not see it, stop and check before moving on.
- **Try your own change** is one small experiment. Pick one, make the change yourself, and predict the result before you run it. This is how you start working beyond the guide.

By the end you should be able to:

- name the power, ground and signal wires of a servo and explain why the servos need their own supply;
- describe how links, joints, actuators and poses fit together;
- test ESP32-C3 servo code in Wokwi before you touch hardware;
- control one joint at a time by angle, and set safe limits for it;
- combine poses into a pick-and-place sequence, and change it yourself.

## Before you start

**Software you need**

- Visual Studio Code with the PlatformIO IDE extension and the Wokwi for VS Code extension.
- Webots R2025a is optional. It appears in the last chapter.

The full install steps are in [SETUP_GUIDE.md](SETUP_GUIDE.md). If something breaks, check [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

**Windows and Mac.** PlatformIO and the Wokwi extension are cross-platform and behave the same way. The Webots launcher script (`scripts/start-webots.ps1`) and its VS Code task are Windows only. On a Mac, open Webots yourself and load `webots/worlds/robot_arm.wbt`. This project has only been tested on Windows so far, so tell your facilitator if a step behaves differently on your machine.

**Hardware per group**

- one ESP32-C3 development board and a USB cable;
- the printed arm parts and four MG996R servos with horns and screws (the facilitator section at the end lists them);
- one regulated 5 V supply that can deliver enough current for four servos;
- jumper wires, with one used as the shared ground;
- one lightweight object, about 25 mm wide, for the final challenge.

## Session plan (3 hours)

| Chapter | Topic | Minutes |
| --- | --- | ---: |
| 0 | Meet the arm | 10 |
| 1 | Joints, links and poses | 15 |
| 2 | Inspect and assemble the arm | 35 |
| | Break | 10 |
| 3 | Build and simulate in Wokwi | 20 |
| 4 | How a servo is controlled | 15 |
| 5 | Wire it safely | 15 |
| 6 | Calibrate one joint at a time | 20 |
| 7 | Poses and smooth motion | 20 |
| 8 | Pick-and-place challenge | 15 |
| 9 | Wrap-up and what next | 5 |

## Chapter 0: Meet the arm (10 min)

### Explain

The arm has four joints. The base turns left and right. The shoulder and elbow tilt up and down. The gripper opens and closes a single jaw. A small computer, the ESP32-C3, tells each servo which angle to go to. Your code decides the angles, and the servos do the moving.

The goal for the day is a pick-and-place: pick up a small object at one spot and put it down at another.

### Do

1. Watch your facilitator run the finished arm with the `p` command.
2. Write down the order of the moves you see. Count how many separate poses the arm passes through.

You should see the arm swing out, lower the jaw, close it, lift, turn, lower, open, and return home.

### Try your own change

Before you read on, list the poses you think the arm needs, in order, and give each a name. You will compare your list with the real one in Chapter 7.

## Chapter 1: Joints, links and poses (15 min)

### Explain

A **link** is a rigid piece. A **joint** connects two links and lets one move relative to the other. An **actuator**, here a servo, makes a joint move. The **end effector** is the part that does the work, here the jaw.

Each independent way the arm can move is a **degree of freedom** (DOF). This arm has four joints, so it has four DOF. The set of places the end effector can reach is its **workspace**.

A **pose** is one value per joint: base, shoulder, elbow and gripper, each as an angle. Describing the arm by its joint angles is called working in **joint space**. Describing it by where the tip is in the room is **task space**. Going from joint angles to tip position is **forward kinematics**. You will use that idea in Chapter 7.

In this project every joint treats **90°** as neutral. At neutral the upper arm points straight up and the forearm is horizontal. For the gripper, 90° means the two jaws touch, and a smaller angle opens the moving jaw.

One fact shapes the whole project: the shoulder axis sits about 87.5 mm above the table. To reach an object on the table, the arm has to lean well forward, with the shoulder near 132° and the elbow near 124°. Poses that look sensible from a standing arm usually do not reach the table at all.

### Do

1. Find the four servos on the arm and label them base, shoulder, elbow and gripper.
2. Name each link and say which two joints it connects.
3. Count the joints. Then hold the arm at neutral (all four at 90°) in your mind and describe its shape.

Do not turn a servo horn by hand. The gears inside can strip.

You should end up with four joints, four servos and a clear picture of which part moves which.

### Try your own change

The upper arm is 118 mm long and the forearm is 110 mm. Predict the longest horizontal distance the tip can reach when both are stretched out flat, then check it against Chapter 7.

## Chapter 2: Inspect and assemble the arm (35 min)

### Explain

Look at how each link is built. It is two flat plates with the servo sandwiched between them, joined by a thin back web. The plates carry the load, and the servo is clamped rather than hanging from one horn.

The upper arm and forearm are each split into two printed pieces, a frame and an outer plate. This lets every piece print flat on the bed with no supports. Three M3 screws join each outer plate to its frame through three posts. The holes in the outer plates are 3.2 mm wide so the screws pass through, and the holes in the posts are 2.6 mm so the screws cut their own thread. The servo pockets leave 0.3 mm of clearance.

### Do

1. Spend 15 minutes inspecting the parts or the CAD model. Find the screw posts, the horn screw holes and the pedestal under the elbow servo.
2. Assemble the arm from the base up: base plate and base servo, turntable on the base servo horn, shoulder servo in the tray, then the upper arm, the elbow servo, the forearm, the gripper servo and the jaws.
3. Join each outer plate to its frame with three M3×12 screws.
4. Check clearances by eye. For each joint, picture it moving through its range and look for parts that would rub or hit the table. You will test real movement in Chapter 6.

You should have a complete arm with no part rubbing another at the neutral pose.

> **Facilitator note:** this order follows how the parts nest in the CAD model. A printed arm has not been assembled yet, so note anything that needs changing and update this chapter.

### Try your own change

Pick one change to the design and predict its effect before you make it. For example, lengthen the moving jaw by 10 mm in CAD. Then open `tools/arm_poses.py`, change `FINGER_TIP` to match, and run `python tools/arm_poses.py`. Compare the new pick poses with the old ones.

## Chapter 3: Build and simulate in Wokwi (20 min)

### Explain

Wokwi simulates the circuit and runs your real firmware on a virtual ESP32-C3. It shows servos turning and lets you type to the firmware, but it does not model mechanics, weight or power. That makes it a safe place to find mistakes before they can hurt a servo.

PlatformIO has two build targets. The `wokwi` environment builds for a virtual board. The `physical` environment builds for the real ESP32-C3-DevKitC-02. You build for `wokwi` now and for `physical` in Chapter 5.

### Do

1. Open the repository root folder in VS Code.
2. Run **PlatformIO: Build**. The default environment is `wokwi`.
3. Check that this file now exists: `.pio/build/wokwi/firmware.bin`.
4. Open `diagram.json` and run **Wokwi: Start Simulator**.
5. Click the terminal built into the Wokwi window and type `?` and press Enter to see the menu. Then try `t` (test every joint), `h` (home) and `p` (pick and place).

You should see all four virtual servos move when you run `t`.

Wokwi runs the compiled file, so after any code change you must build again and restart the simulator.

### Try your own change

Edit one pose in `src/main.cpp`, for example change the base angle of `PICK_APPROACH` from 45 to 60. Rebuild, restart Wokwi, run `p`, and watch which servo behaves differently.

## Chapter 4: How a servo is controlled (15 min)

### Explain

A hobby servo contains a motor, gears, a position sensor and a small controller. The controller drives the motor until the output shaft matches the position it was told to hold.

You give it that position as a **pulse**. The ESP32 sends a short high pulse about 50 times a second, once every 20 ms. The **width** of the pulse is the command. A pulse of roughly 1 ms means one end of the range, about 1.5 ms means the middle, and about 2 ms means the other end. This is pulse-width modulation (PWM). The information is in the pulse width, not in an average voltage.

The ESP32Servo library creates these pulses on any GPIO pin. The firmware then works in angles, and the library converts them. The firmware starts with a conservative pulse range of 1000 to 2000 µs, set in `SERVO_MIN_US` and `SERVO_MAX_US` at the top of `src/main.cpp`. Real servos differ, so you will check it against your own servos after wiring.

The code holds one setting per joint in a `CONFIG` table: the pin, the safe minimum and maximum angle, whether the direction is inverted, and a trim offset. A `Pose` is four angles. `constrainPose()` clamps every angle to its limits, so a bad pose cannot drive a joint past its range.

### Do

1. Open `src/main.cpp`. Find the `CONFIG` table, `writeJoint()`, `constrainPose()` and `moveTo()`.
2. Match the pins to the joints: GPIO 3 is the base, GPIO 4 the shoulder, GPIO 5 the elbow, GPIO 6 the gripper.
3. Open `diagram.json` and trace each servo signal wire back to its GPIO.

You should find the same four pin numbers in the code and in the diagram.

### Try your own change

Add a new `w` command that waves the arm. Define two poses above the limit-checking code:

```cpp
const Pose WAVE_A = { 90, 90, 60, 40 };
const Pose WAVE_B = { 90, 90, 120, 40 };
```

Then add this case in `loop()`, next to the other commands:

```cpp
    case 'w':
      go(WAVE_A, 400);
      go(WAVE_B, 400);
      go(HOME, 600);
      break;
```

Rebuild, restart Wokwi and type `w`. Then change the numbers to make a different gesture.

## Chapter 5: Wire it safely (15 min)

### Explain

A servo has three wires: **power** (usually red), **ground** (usually brown or black) and **signal** (usually orange, yellow or white). The signal carries the pulse. Power and ground feed the motor.

A servo under load can draw far more current than a USB port or the ESP32 board can supply. Never power four servos from the ESP32 5 V pin. Use the separate regulated 5 V supply for servo power.

The servo supply and the ESP32 must **share a ground**. The pulse is a voltage measured against ground, so the servo can only read it correctly if both sides use the same zero.

### Do

Wire with all power off.

| Joint | ESP32-C3 GPIO |
| --- | ---: |
| Base | 3 |
| Shoulder | 4 |
| Elbow | 5 |
| Gripper | 6 |

1. Connect each servo signal wire to its GPIO from the table.
2. Connect each servo power and ground wire to the external supply, not to the ESP32.
3. Connect the external supply ground to an ESP32 GND pin.
4. Compare your wiring with `diagram.json`, wire by wire.
5. Where practical, remove the servo horns for the first power-on so nothing can strike a mechanical stop.
6. Connect the ESP32 to the computer by USB. In PlatformIO, run **Project Tasks, physical, Upload**.
7. Switch the servo supply on, with a hand near the switch. Type `?` in a serial terminal at 115200 baud.

You should see the menu text, and the servos should move to the home pose one at a time.

If a joint stalls, vibrates, hits a stop or gets hot, switch the servo supply off immediately.

### Try your own change

Draw the wiring diagram from memory, then compare it with `diagram.json`. Then plan a way to cut servo power quickly in an emergency, such as a switch in the supply line, and add it to your drawing.

## Chapter 6: Calibrate one joint at a time (20 min)

### Explain

The example angle limits are starting values, not facts about your arm. Every printed arm differs a little, and a joint that hits a mechanical stop can strip a gear. **Calibration** means finding the range each joint can move freely on your own arm and telling the code to stay inside it.

Two more settings live in the same table. If a servo turns the wrong way for how it is mounted, set its `invert` to `true`. If a horn was fitted a few degrees off, use `trim` instead of editing every pose.

For the gripper, 90° means the jaws touch, so the starting maximum is 88°. Smaller angles open the jaw.

### Do

1. Start at `HOME`, with all joints at 90°.
2. Select one joint with `b`, `s`, `e` or `g`.
3. Jog it by 1° with `+` and `-`, or by 5° with `]` and `[`.
4. Note the angle at each end where the joint still moves freely, and stop before it strains.
5. Leave a safety margin at both ends, then enter the limits in the `CONFIG` table in `src/main.cpp`.
6. Repeat for all four joints. Then run `t` to move each joint a little either side of its position.
7. Check the pulse range. If any joint cannot reach its full range, adjust `SERVO_MIN_US` and `SERVO_MAX_US`, then calibrate the limits again.

Type `x` at any time to stop a movement.

You should end with a written minimum and maximum for every joint, and `t` should run without strain.

### Try your own change

Find which of your joints, if any, needs `invert` or `trim`. Make the change, rebuild, upload, and confirm with `t` that every joint moves the expected way.

## Chapter 7: Poses and smooth motion (20 min)

### Explain

Moving from one pose to another needs more than jumping to the new angles. The code uses **linear interpolation**. It splits the move into 50 small steps. At step number i out of 50, each joint is at:

```text
angle = start + (target - start) * (i / 50)
```

Because every joint uses the same fraction, they all start and finish together, and the motion looks coordinated. The blocking delay between steps sets the duration. In `src/main.cpp`, turning `EASED_MOTION` on uses a smoother curve that starts and stops gently.

The eight poses are `HOME`, `PICK_APPROACH`, `PICK`, `GRAB`, `LIFT`, `PLACE_APPROACH`, `PLACE` and `RELEASE`. They came from forward kinematics. Given the shoulder and elbow angles and the link lengths, you can compute where the jaw tip is. `tools/arm_poses.py` runs that calculation for every allowed shoulder and elbow angle and keeps the combinations that put the tip at the height and distance you ask for, while keeping the arm clear of the table.

### Do

1. Run `python tools/arm_poses.py` and read the table of poses and tip positions.
2. Check that the poses in `src/main.cpp` match, then tune them in this order: `HOME`, `PICK_APPROACH`, `PICK`, `GRAB`, `LIFT`, `PLACE_APPROACH`, `PLACE`, `RELEASE`.
3. Fine-tune each pose with the jog keys. After each one, press `c` to print the pose you reached, and paste it into the code.
4. Test each new pose without an object before you run the full sequence. Keep a hand near the servo-power switch.

You should be able to run `p` with an empty table and see the jaw reach the pick spot and the drop spot without touching the table.

### Try your own change

Move the object. Run `python tools/arm_poses.py --reach 140 --pick-height 20`, paste the new lines into the code, and test. Or turn on `EASED_MOTION` and compare how the two kinds of motion feel.

## Chapter 8: Pick-and-place challenge (15 min)

### Explain

You now have everything the sequence needs: limits that protect the joints, poses that put the jaw where you want it, and interpolation that moves between them. The `GRAB` pose is set to 58°, an estimate for closing the jaw on a 25 mm object. It has not been measured on a real arm, so expect to tune it for yours.

### Do

1. Place the object at the pick spot, about 110 mm in front of the base.
2. Run `p`. If anything goes wrong, type `x` to stop.
3. Watch where it fails: a missed grab, a drop, or a collision. Fix the pose that causes it and run again.

You should see the arm pick up the object and set it down at the drop spot.

### Try your own change

Move the drop location, or build your own sequence: pick from one spot, place at another, then return home. Time your best run.

## Chapter 9: Wrap-up and what next (5 min)

### Explain

Look back at what you built: a mechanical design, a circuit, a controller and a calibration routine. Each one could break the arm on its own, which is why the project simulates first, limits every joint, and tests one change at a time.

### Do

1. Return the arm to `HOME` and switch off servo power before changing any wiring.
2. Write down the calibrated limits for your arm.
3. Check that both PlatformIO environments still build before you share your changes.
4. Commit working pose changes on a separate branch, or keep a configuration per arm.

### Try your own change

Choose one extension to take further:

- Compare eased and linear motion over a longer move.
- Add potentiometers or a joystick for manual control.
- Store calibrated limits in nonvolatile memory.
- Add a physical emergency-stop input.
- Replace blocking delays with a state machine so a stop command is always instant.
- Add inverse kinematics, where you give the tip position and the code finds the angles.

**Optional: a digital twin in Webots.** Webots simulates the arm's mechanics in 3D, using the same poses as the firmware. Open `webots/worlds/robot_arm.wbt`, click the 3D view, then press `P`, `H`, `T` and `X`, and jog with `B`, `S`, `E`, `G` and `+` and `-`. A pose you tune in Webots carries over to the firmware, but it does not model servo torque, so always test on the real arm. The tools are in [SETUP_GUIDE.md](SETUP_GUIDE.md).

## Facilitator preparation

**Printed parts**

The seven printed parts are the base plate, the turntable, the upper-arm plate and frame, the forearm frame, the forearm outer plate with the fixed jaw, and the moving jaw. Each arm also needs four MG996R servos with horns and fasteners, and six M3×12 screws.

The upper arm and forearm are split so every part prints flat with no supports. Orient the parts like this:

| Part | Print it like this |
| --- | --- |
| Upper-arm plate A | outer face down (a flat plate) |
| Upper-arm frame | the plate with the engraved rings down; the back web and three screw posts point up |
| Forearm frame | outer face down; the back web and three screw posts point up |
| Forearm outer plate with the fixed jaw | the flat inner face down; the jaw points up |
| Base plate | the round plate on the bed with the feet pointing up |
| Turntable | disc down |
| Moving jaw | either face down |

The forearm outer plate is 180 mm long, so on a 180 mm bed it must go diagonally. Print one link first and test-fit a servo before you print the rest.

**Before the session**

1. Clone this repository on every workshop computer.
2. Run **PlatformIO: Build** and confirm the `wokwi` environment builds.
3. Start Wokwi and confirm that `t` moves all four simulated servos in the built-in terminal.
4. Check every physical arm for loose fasteners and binding joints.
5. Label the base, shoulder, elbow and gripper leads.
6. Verify each external power supply and the common-ground connection.
7. Mark a safe pickup area and drop area.
8. Keep one fully assembled reference arm ready for demonstrations.

Do not hand out arms with unverified poses. The values in the repository are starting points for simulation and calibration.
