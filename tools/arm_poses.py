"""Work out servo angles for pick-and-place poses.

The arm moves in one vertical plane once the base has turned, so two servo
angles (shoulder and elbow) decide where the finger tip is. This script
searches those angles for a tip position measured from the base axis, with
the table at height 0 (the very bottom of the arm base).

Usage:
    python tools/arm_poses.py                      # defaults: 110 mm reach
    python tools/arm_poses.py --reach 140 --pick-height 20

Servo angle 90 = neutral (upper arm vertical, forearm horizontal), and a
larger angle leans the joint forward / folds the forearm down. For the
gripper, 90 = jaws touching and smaller angles open the jaw.
Dimensions come from the Fusion model; update them if the CAD changes.
"""
import argparse
import math

SHOULDER_HEIGHT = 87.5      # mm, shoulder axis above the table
UPPER_ARM = 118.0           # mm, shoulder axis -> elbow axis
FOREARM = 110.0             # mm, elbow axis -> gripper axis
# Two straight jaws point forward along the forearm, so the tip that reaches the
# object is the end of the fixed (lower) jaw, measured from the elbow axis.
FINGER_TIP = (FOREARM + 56.0, -8.4)
# Forearm plates plus both jaws (moving jaw shown closed).
FOREARM_OUTLINE = [
    (0, -14), (0, 14), (128, -14), (128, 14),
    (FOREARM + 13, -12.4), (FOREARM + 52, -12.4), (FOREARM + 56, -8.4),
    (FOREARM + 56, 0), (FOREARM + 52, 4),
]
MIN_CLEARANCE = 3.0         # mm, keep every forearm point this far above the table
SERVO_LIMITS = (30, 150)    # same as the firmware limits


def arm(shoulder, elbow):
    """Return (tip_x, tip_z, lowest_z) for the given servo angles."""
    ts = math.radians(shoulder - 90)
    phi = ts + math.radians(elbow - 90)
    ex = UPPER_ARM * math.sin(ts)
    ez = SHOULDER_HEIGHT + UPPER_ARM * math.cos(ts)
    c, s = math.cos(phi), math.sin(phi)

    def place(a, b):
        return ex + a * c + b * s, ez - a * s + b * c

    tip = place(*FINGER_TIP)
    lowest = min(place(a, b)[1] for a, b in FOREARM_OUTLINE + [FINGER_TIP])
    return tip[0], tip[1], lowest


def solve(reach, height, near=None, tolerance=4.0):
    best = None
    lo, hi = SERVO_LIMITS
    for shoulder in range(lo, hi + 1):
        for elbow in range(lo, hi + 1):
            x, z, lowest = arm(shoulder, elbow)
            if lowest < MIN_CLEARANCE:
                continue
            error = math.hypot(x - reach, z - height)
            if error > tolerance:
                continue
            cost = error * 5
            if near:
                cost += abs(shoulder - near[0]) + abs(elbow - near[1])
            if best is None or cost < best[0]:
                best = (cost, shoulder, elbow, x, z)
    return best


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--reach", type=float, default=110.0, help="tip distance from base axis, mm")
    p.add_argument("--pick-height", type=float, default=12.0, help="jaw-tip height at the object, mm")
    p.add_argument("--approach-height", type=float, default=70.0, help="tip height while travelling, mm")
    p.add_argument("--base-pick", type=int, default=45)
    p.add_argument("--base-place", type=int, default=135)
    p.add_argument("--gripper-open", type=int, default=40,
                   help="servo angle with the jaw open (about 50 degrees of opening)")
    p.add_argument("--gripper-closed", type=int, default=58,
                   help="servo angle that grips the object (90 = jaws touching)")
    a = p.parse_args()

    low = solve(a.reach, a.pick_height)
    if low is None:
        raise SystemExit("No safe servo angles reach that point. Try a different reach/height.")
    high = solve(a.reach, a.approach_height, (low[1], low[2]))
    if high is None:
        raise SystemExit("No safe approach pose found. Try a lower --approach-height.")

    print("Pose        base shoulder elbow gripper   tip (x, z) mm")
    rows = [
        ("HOME", 90, 90, 90, a.gripper_open, arm(90, 90)),
        ("PICK_APPROACH", a.base_pick, high[1], high[2], a.gripper_open, arm(high[1], high[2])),
        ("PICK", a.base_pick, low[1], low[2], a.gripper_open, arm(low[1], low[2])),
        ("GRAB", a.base_pick, low[1], low[2], a.gripper_closed, arm(low[1], low[2])),
        ("LIFT", a.base_pick, high[1], high[2], a.gripper_closed, arm(high[1], high[2])),
        ("PLACE_APPROACH", a.base_place, high[1], high[2], a.gripper_closed, arm(high[1], high[2])),
        ("PLACE", a.base_place, low[1], low[2], a.gripper_closed, arm(low[1], low[2])),
        ("RELEASE", a.base_place, low[1], low[2], a.gripper_open, arm(low[1], low[2])),
    ]
    for name, base, shoulder, elbow, grip, (x, z, _) in rows:
        print("%-15s %4d %8d %5d %7d   (%.0f, %.0f)" % (name, base, shoulder, elbow, grip, x, z))

    print("\n// C++ (src/main.cpp)")
    for name, base, shoulder, elbow, grip, _ in rows:
        print("const Pose %s = { %d, %d, %d, %d };" % (name, base, shoulder, elbow, grip))
    print("\n# Python (arm_controller.py)")
    for name, base, shoulder, elbow, grip, _ in rows:
        print('%s = {"base": %d, "shoulder": %d, "elbow": %d, "gripper": %d}' % (name, base, shoulder, elbow, grip))


if __name__ == "__main__":
    main()
