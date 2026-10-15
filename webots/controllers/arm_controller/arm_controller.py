from math import radians
from controller import Robot


# ============================================================
# WEBOTS SETUP
# ============================================================

robot = Robot()
TIME_STEP = int(robot.getBasicTimeStep())

keyboard = robot.getKeyboard()
keyboard.enable(TIME_STEP)


# ============================================================
# MOTOR AND SENSOR NAMES
# These names must match robot_arm.wbt exactly.
# ============================================================

JOINTS = ["base", "shoulder", "elbow", "gripper"]

motors = {
    "base": robot.getDevice("base_motor"),
    "shoulder": robot.getDevice("shoulder_motor"),
    "elbow": robot.getDevice("elbow_motor"),
    "gripper": robot.getDevice("gripper_motor"),
}

sensors = {
    "base": robot.getDevice("base_sensor"),
    "shoulder": robot.getDevice("shoulder_sensor"),
    "elbow": robot.getDevice("elbow_sensor"),
    "gripper": robot.getDevice("gripper_sensor"),
}

for sensor in sensors.values():
    sensor.enable(TIME_STEP)

motors["base"].setVelocity(2.0)
motors["shoulder"].setVelocity(2.0)
motors["elbow"].setVelocity(2.0)
motors["gripper"].setVelocity(3.0)


# ============================================================
# SERVO LIMITS
# These match src/main.cpp.
# ============================================================

LIMITS = {
    "base": (20, 160),
    "shoulder": (30, 150),
    "elbow": (30, 150),
    "gripper": (20, 90),
}


# ============================================================
# POSES
# These match the ESP32 firmware (src/main.cpp).
#
# Angles are servo degrees; 90 = neutral (upper arm vertical,
# forearm horizontal). They were worked out for an object on
# the table about 110 mm in front of the base axis.
# Regenerate with:  python tools/arm_poses.py --reach 140
# ============================================================

HOME = {"base": 90, "shoulder": 90, "elbow": 90, "gripper": 30}
PICK_APPROACH = {"base": 45, "shoulder": 97, "elbow": 124, "gripper": 30}
PICK = {"base": 45, "shoulder": 135, "elbow": 112, "gripper": 30}
GRAB = {"base": 45, "shoulder": 135, "elbow": 112, "gripper": 75}
LIFT = {"base": 45, "shoulder": 97, "elbow": 124, "gripper": 75}
PLACE_APPROACH = {"base": 135, "shoulder": 97, "elbow": 124, "gripper": 75}
PLACE = {"base": 135, "shoulder": 135, "elbow": 112, "gripper": 75}
RELEASE = {"base": 135, "shoulder": 135, "elbow": 112, "gripper": 30}

current_pose = HOME.copy()
selected_joint = "base"


# ============================================================
# CONVERSION AND LIMIT FUNCTIONS
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def constrain_pose(pose):
    result = {}

    for joint, value in pose.items():
        minimum, maximum = LIMITS[joint]
        result[joint] = clamp(value, minimum, maximum)

    return result


def servo_to_joint(joint, servo_degrees):
    """
    Convert physical-servo degrees into Webots joint radians.

    The base, shoulder and elbow use 90 degrees as the zero
    position. The gripper maps 20-90 servo degrees onto
    0 to +35 Webots degrees: 0 is fully open and larger angles
    close the finger towards the fixed jaw.
    """

    if joint == "gripper":
        fraction = (
            (servo_degrees - LIMITS["gripper"][0])
            / (LIMITS["gripper"][1] - LIMITS["gripper"][0])
        )

        return radians(35.0 * fraction)

    return radians(servo_degrees - 90.0)


# ============================================================
# MOTOR COMMANDS
# ============================================================

def write_pose(pose):
    pose = constrain_pose(pose)

    for joint, servo_degrees in pose.items():
        target_radians = servo_to_joint(joint, servo_degrees)
        motors[joint].setPosition(target_radians)


# ============================================================
# STOP COMMAND
# Press X in the 3D view to stop the current movement.
# Other keys pressed during a movement are ignored.
# ============================================================

def stop_requested():
    stop = False

    while True:
        key = keyboard.getKey()

        if key == -1:
            return stop

        if chr(key & 0xFF).lower() == "x":
            stop = True


def wait_ms(duration_ms):
    """Wait without blocking the stop key. False = stopped."""

    steps = max(1, int(duration_ms / TIME_STEP))

    for _ in range(steps):
        if stop_requested():
            return False

        if robot.step(TIME_STEP) == -1:
            return False

    return True


def move_to(target, duration_ms):
    """
    Linearly interpolate every joint from the current pose to
    the target pose. This mirrors moveTo() in the ESP32 code.
    Returns False if the movement was stopped.
    """

    global current_pose

    target = constrain_pose(target)
    start = current_pose.copy()

    steps = max(1, int(duration_ms / TIME_STEP))

    for step in range(1, steps + 1):
        if stop_requested():
            print("STOPPED")
            return False

        progress = step / steps

        intermediate = {
            joint: start[joint]
            + (target[joint] - start[joint]) * progress
            for joint in start
        }

        write_pose(intermediate)
        current_pose = constrain_pose(intermediate)

        if robot.step(TIME_STEP) == -1:
            return False

    current_pose = target.copy()
    return True


def go(target, duration_ms, pause_ms=0):
    """Move, then pause. Returns False if stopped."""

    return move_to(target, duration_ms) and (
        pause_ms == 0 or wait_ms(pause_ms)
    )


# ============================================================
# SERVO TEST
# ============================================================

def test_servos():
    print("Testing all joints (X = stop)")

    offsets = {"base": 20, "shoulder": 20, "elbow": 20, "gripper": 40}

    for joint in JOINTS:
        print("Testing", joint)

        before = current_pose.copy()
        low = {**before, joint: before[joint] - offsets[joint]}
        high = {**before, joint: before[joint] + offsets[joint]}

        if not (go(low, 800) and go(high, 1000) and go(before, 800)):
            print("Test stopped")
            return

    go(HOME, 1000)
    print("Test complete")


# ============================================================
# PICK-AND-PLACE SEQUENCE
# ============================================================

def pick_and_place():
    print("Starting pick and place (X = stop)")

    finished = (
        go(HOME, 1000, 500)
        and go(PICK_APPROACH, 1000, 300)
        and go(PICK, 800, 300)
        and go(GRAB, 500, 500)
        and go(LIFT, 1000, 300)
        and go(PLACE_APPROACH, 1200, 300)
        and go(PLACE, 800, 300)
        and go(RELEASE, 500, 500)
        and go(PLACE_APPROACH, 800)
        and go(HOME, 1200)
    )

    print("Sequence complete" if finished else "Sequence stopped")


# ============================================================
# CALIBRATION (jog one joint at a time)
# ============================================================

def select_joint(joint):
    global selected_joint

    selected_joint = joint
    print("Selected %s at %d" % (joint, current_pose[joint]))


def jog(delta):
    global current_pose

    minimum, maximum = LIMITS[selected_joint]
    wanted = current_pose[selected_joint] + delta
    allowed = clamp(wanted, minimum, maximum)

    current_pose = {**current_pose, selected_joint: allowed}
    write_pose(current_pose)

    note = "  (at limit)" if allowed != wanted else ""
    print("%s = %d%s" % (selected_joint, allowed, note))


def print_pose():
    p = current_pose
    print(
        'MY_POSE = {"base": %d, "shoulder": %d, "elbow": %d, "gripper": %d}'
        % (round(p["base"]), round(p["shoulder"]),
           round(p["elbow"]), round(p["gripper"]))
    )


# ============================================================
# USER INTERFACE
# ============================================================

def print_menu():
    print()
    print("===========================")
    print(" WEBOTS ROBOT ARM CONTROL")
    print("===========================")
    print("Click the 3D view, then press:")
    print("H = HOME")
    print("T = Test servos")
    print("P = Pick and place")
    print("X = STOP the current move")
    print("---------------------------")
    print("Calibrate one joint:")
    print("B/S/E/G = select base/shoulder/")
    print("          elbow/gripper")
    print("+ / -   = jog 1 degree")
    print("] / [   = jog 5 degrees")
    print("C       = print current pose")
    print("---------------------------")
    print("? = Show this menu")
    print("===========================")


write_pose(HOME)
robot.step(TIME_STEP)
print_menu()


# ============================================================
# MAIN LOOP
# ============================================================

while robot.step(TIME_STEP) != -1:
    key = keyboard.getKey()

    if key == -1:
        continue

    # Modifier information may occupy higher bits.
    character = chr(key & 0xFF).lower()

    if character == "h":
        print("Going HOME")
        move_to(HOME, 1000)

    elif character == "t":
        test_servos()

    elif character == "p":
        pick_and_place()

    elif character == "x":
        print("Nothing is moving")

    elif character == "b":
        select_joint("base")

    elif character == "s":
        select_joint("shoulder")

    elif character == "e":
        select_joint("elbow")

    elif character == "g":
        select_joint("gripper")

    elif character in ("+", "="):
        jog(1)

    elif character in ("-", "_"):
        jog(-1)

    elif character == "]":
        jog(5)

    elif character == "[":
        jog(-5)

    elif character == "c":
        print_pose()

    elif character == "?":
        print_menu()
