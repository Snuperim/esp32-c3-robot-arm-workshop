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
# These match the ESP32 firmware.
# ============================================================

HOME = {
    "base": 90,
    "shoulder": 90,
    "elbow": 90,
    "gripper": 30,
}

PICK_APPROACH = {
    "base": 45,
    "shoulder": 95,
    "elbow": 80,
    "gripper": 30,
}

PICK = {
    "base": 45,
    "shoulder": 120,
    "elbow": 60,
    "gripper": 30,
}

GRAB = {
    "base": 45,
    "shoulder": 120,
    "elbow": 60,
    "gripper": 75,
}

LIFT = {
    "base": 45,
    "shoulder": 80,
    "elbow": 90,
    "gripper": 75,
}

PLACE_APPROACH = {
    "base": 135,
    "shoulder": 85,
    "elbow": 90,
    "gripper": 75,
}

PLACE = {
    "base": 135,
    "shoulder": 115,
    "elbow": 65,
    "gripper": 75,
}

RELEASE = {
    "base": 135,
    "shoulder": 115,
    "elbow": 65,
    "gripper": 30,
}

current_pose = HOME.copy()


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
    0 to -35 Webots degrees.
    """

    if joint == "gripper":
        fraction = (
            (servo_degrees - LIMITS["gripper"][0])
            / (LIMITS["gripper"][1] - LIMITS["gripper"][0])
        )

        return radians(-35.0 * fraction)

    return radians(servo_degrees - 90.0)


# ============================================================
# MOTOR COMMANDS
# ============================================================

def write_pose(pose):
    pose = constrain_pose(pose)

    for joint, servo_degrees in pose.items():
        target_radians = servo_to_joint(joint, servo_degrees)
        motors[joint].setPosition(target_radians)


def wait_ms(duration_ms):
    steps = max(1, int(duration_ms / TIME_STEP))

    for _ in range(steps):
        if robot.step(TIME_STEP) == -1:
            return False

    return True


def move_to(target, duration_ms):
    """
    Linearly interpolate every joint from the current pose to
    the target pose. This mirrors moveTo() in the ESP32 code.
    """

    global current_pose

    target = constrain_pose(target)
    start = current_pose.copy()

    steps = max(1, int(duration_ms / TIME_STEP))

    for step in range(1, steps + 1):
        progress = step / steps

        intermediate = {
            joint: start[joint]
            + (target[joint] - start[joint]) * progress
            for joint in start
        }

        write_pose(intermediate)

        if robot.step(TIME_STEP) == -1:
            return False

    current_pose = target.copy()
    return True


# ============================================================
# SERVO TEST
# ============================================================

def test_servos():
    print("Testing base")
    move_to({**current_pose, "base": 70}, 800)
    move_to({**current_pose, "base": 110}, 800)
    move_to({**current_pose, "base": 90}, 800)

    print("Testing shoulder")
    move_to({**current_pose, "shoulder": 70}, 800)
    move_to({**current_pose, "shoulder": 110}, 800)
    move_to({**current_pose, "shoulder": 90}, 800)

    print("Testing elbow")
    move_to({**current_pose, "elbow": 70}, 800)
    move_to({**current_pose, "elbow": 110}, 800)
    move_to({**current_pose, "elbow": 90}, 800)

    print("Testing gripper")
    move_to({**current_pose, "gripper": 30}, 800)
    move_to({**current_pose, "gripper": 70}, 800)
    move_to({**current_pose, "gripper": 30}, 800)

    move_to(HOME, 1000)
    print("Test complete")


# ============================================================
# PICK-AND-PLACE SEQUENCE
# ============================================================

def pick_and_place():
    print("Starting pick and place")

    move_to(HOME, 1000)
    wait_ms(500)

    move_to(PICK_APPROACH, 1000)
    wait_ms(300)

    move_to(PICK, 800)
    wait_ms(300)

    move_to(GRAB, 500)
    wait_ms(500)

    move_to(LIFT, 1000)
    wait_ms(300)

    move_to(PLACE_APPROACH, 1200)
    wait_ms(300)

    move_to(PLACE, 800)
    wait_ms(300)

    move_to(RELEASE, 500)
    wait_ms(500)

    move_to(PLACE_APPROACH, 800)
    move_to(HOME, 1200)

    print("Sequence complete")


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

    elif character == "?":
        print_menu()