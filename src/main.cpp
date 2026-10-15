#include <Arduino.h>
#include <ESP32Servo.h>

// ======================================================
// ROBOT ARM - ESP32-C3
// Base + Shoulder + Elbow + Gripper
//
// Angles are servo degrees (0-180).
// 90 = neutral: upper arm vertical, forearm horizontal.
// ======================================================

// -------------------- SERVO PULSE RANGE ----------------
// Starting conservatively with 1000-2000 us.
// Check your own servos after wiring and change these two
// numbers only if the servo cannot reach its full range.

const int SERVO_MIN_US = 1000;
const int SERVO_MAX_US = 2000;

// -------------------- JOINT SETTINGS -------------------
// THESE ARE STARTING VALUES ONLY.
// Calibrate each joint on the real robot before using the
// automatic sequence.
//
//   minAngle / maxAngle : safe range for this joint
//   invert              : true if + angle moves the joint
//                         the wrong way for your mounting
//   trim                : degrees added to correct a horn
//                         that was fitted a little off

enum JointId { BASE, SHOULDER, ELBOW, GRIPPER, JOINT_COUNT };

struct JointConfig {
  const char* name;
  int pin;
  int minAngle;
  int maxAngle;
  bool invert;
  int trim;
};

const JointConfig CONFIG[JOINT_COUNT] = {
  // name        pin  min  max  invert trim
  { "base",      3,   20, 160, false,  0 },
  { "shoulder",  4,   30, 150, false,  0 },
  { "elbow",     5,   30, 150, false,  0 },
  { "gripper",   6,   20,  90, false,  0 },
};

Servo servos[JOINT_COUNT];

// Set to true for smoother starts and stops.
const bool EASED_MOTION = false;

// -------------------- ROBOT POSE -----------------------

struct Pose {
  int base;
  int shoulder;
  int elbow;
  int gripper;
};

int getAngle(const Pose& p, int joint) {
  switch (joint) {
    case BASE:     return p.base;
    case SHOULDER: return p.shoulder;
    case ELBOW:    return p.elbow;
    default:       return p.gripper;
  }
}

void setAngle(Pose& p, int joint, int value) {
  switch (joint) {
    case BASE:     p.base = value;     break;
    case SHOULDER: p.shoulder = value; break;
    case ELBOW:    p.elbow = value;    break;
    default:       p.gripper = value;  break;
  }
}

Pose currentPose = { 90, 90, 90, 30 };

// ======================================================
// PREDEFINED ROBOT POSITIONS
//
// These were worked out for an object on the table about
// 110 mm in front of the base axis (table = bottom of the
// arm base). Regenerate them for another position with:
//
//   python tools/arm_poses.py --reach 140
//
// Always test each pose without an object first.
// ======================================================

// Neutral safe position
const Pose HOME = { 90, 90, 90, 30 };

// Hovering above the pickup object
const Pose PICK_APPROACH = { 45, 97, 124, 30 };

// Lowered onto the object, gripper open
const Pose PICK = { 45, 135, 112, 30 };

// Object gripped
const Pose GRAB = { 45, 135, 112, 75 };

// Raise the object
const Pose LIFT = { 45, 97, 124, 75 };

// Above the drop zone
const Pose PLACE_APPROACH = { 135, 97, 124, 75 };

// Lowered into the drop position
const Pose PLACE = { 135, 135, 112, 75 };

// Release the object
const Pose RELEASE = { 135, 135, 112, 30 };

// ======================================================
// LIMIT FUNCTION
// ======================================================

Pose constrainPose(Pose p) {
  for (int j = 0; j < JOINT_COUNT; j++) {
    setAngle(p, j,
             constrain(getAngle(p, j),
                       CONFIG[j].minAngle,
                       CONFIG[j].maxAngle));
  }
  return p;
}

// ======================================================
// WRITE TO THE SERVOS
// ======================================================

void writeJoint(int joint, int angle) {
  int out = constrain(angle,
                      CONFIG[joint].minAngle,
                      CONFIG[joint].maxAngle);

  if (CONFIG[joint].invert) {
    out = 180 - out;
  }

  out = constrain(out + CONFIG[joint].trim, 0, 180);

  servos[joint].write(out);
}

void writePose(Pose p) {
  p = constrainPose(p);

  for (int j = 0; j < JOINT_COUNT; j++) {
    writeJoint(j, getAngle(p, j));
  }

  currentPose = p;
}

// ======================================================
// STOP COMMAND
//
// Typing x (then Enter) stops the current movement.
// Anything else typed while the arm is moving is ignored.
// ======================================================

bool stopRequested() {
  bool stop = false;

  while (Serial.available()) {
    char c = Serial.read();
    if (c == 'x' || c == 'X') {
      stop = true;
    }
  }

  return stop;
}

// Wait without blocking the stop command.
// Returns false if the user asked to stop.
bool waitMs(int durationMs) {
  for (int waited = 0; waited < durationMs; waited += 10) {
    if (stopRequested()) {
      return false;
    }
    delay(10);
  }
  return true;
}

// ======================================================
// SMOOTH MOVEMENT
// Returns false if the user stopped it with x.
// ======================================================

bool moveTo(Pose target, int durationMs) {
  target = constrainPose(target);

  Pose start = currentPose;

  const int steps = 50;

  for (int i = 1; i <= steps; i++) {
    if (stopRequested()) {
      Serial.println("STOPPED");
      return false;
    }

    float progress = (float)i / (float)steps;

    if (EASED_MOTION) {
      progress = progress * progress * (3.0f - 2.0f * progress);
    }

    Pose intermediate;

    for (int j = 0; j < JOINT_COUNT; j++) {
      int from = getAngle(start, j);
      int to = getAngle(target, j);
      setAngle(intermediate, j, from + (to - from) * progress);
    }

    writePose(intermediate);

    delay(durationMs / steps);
  }

  currentPose = target;
  return true;
}

// Move, then pause. Returns false if stopped.
bool go(Pose target, int durationMs, int pauseMs = 0) {
  return moveTo(target, durationMs) && waitMs(pauseMs);
}

// ======================================================
// PICK AND PLACE SEQUENCE
// ======================================================

void pickAndPlace() {
  Serial.println("Starting pick and place (x = stop)");

  bool finished =
      go(HOME, 1000, 500)             // start from HOME
      && go(PICK_APPROACH, 1000, 300) // hover over the object
      && go(PICK, 800, 300)           // lower onto it
      && go(GRAB, 500, 500)           // close the gripper
      && go(LIFT, 1000, 300)          // raise it
      && go(PLACE_APPROACH, 1200, 300)// swing to the drop zone
      && go(PLACE, 800, 300)          // lower it
      && go(RELEASE, 500, 500)        // open the gripper
      && go(PLACE_APPROACH, 800)      // move away
      && go(HOME, 1200);              // return HOME

  Serial.println(finished ? "Sequence complete"
                          : "Sequence stopped");
}

// ======================================================
// SERVO TEST
// ======================================================

void testServos() {
  Serial.println("Testing all joints (x = stop)");

  const int offsets[JOINT_COUNT] = { 20, 20, 20, 40 };

  for (int j = 0; j < JOINT_COUNT; j++) {
    Serial.print("Testing ");
    Serial.println(CONFIG[j].name);

    Pose a = currentPose;
    Pose b = currentPose;

    setAngle(a, j, getAngle(currentPose, j) - offsets[j]);
    setAngle(b, j, getAngle(currentPose, j) + offsets[j]);

    Pose home = currentPose;

    if (!(go(a, 800) && go(b, 1000) && go(home, 800))) {
      Serial.println("Test stopped");
      return;
    }
  }

  go(HOME, 1000);
  Serial.println("Test complete");
}

// ======================================================
// CALIBRATION (jog one joint at a time)
// ======================================================

int selectedJoint = BASE;

void selectJoint(int joint) {
  selectedJoint = joint;
  Serial.print("Selected ");
  Serial.print(CONFIG[joint].name);
  Serial.print(" at ");
  Serial.println(getAngle(currentPose, joint));
}

void jog(int delta) {
  Pose p = currentPose;
  int wanted = getAngle(p, selectedJoint) + delta;
  int allowed = constrain(wanted,
                          CONFIG[selectedJoint].minAngle,
                          CONFIG[selectedJoint].maxAngle);

  setAngle(p, selectedJoint, allowed);
  writePose(p);

  Serial.print(CONFIG[selectedJoint].name);
  Serial.print(" = ");
  Serial.print(allowed);

  if (allowed != wanted) {
    Serial.print("  (at limit)");
  }

  Serial.println();
}

// Print the current pose so it can be pasted above.
void printPose() {
  Serial.print("const Pose MY_POSE = { ");
  Serial.print(currentPose.base);
  Serial.print(", ");
  Serial.print(currentPose.shoulder);
  Serial.print(", ");
  Serial.print(currentPose.elbow);
  Serial.print(", ");
  Serial.print(currentPose.gripper);
  Serial.println(" };");
}

// ======================================================
// SERIAL MENU
// ======================================================

void printMenu() {
  Serial.println();
  Serial.println("===========================");
  Serial.println(" ROBOT ARM CONTROL");
  Serial.println("===========================");
  Serial.println("h = HOME");
  Serial.println("t = Test servos");
  Serial.println("p = Pick and place");
  Serial.println("x = STOP the current move");
  Serial.println("---------------------------");
  Serial.println("Calibrate one joint:");
  Serial.println("b/s/e/g = select base/shoulder/");
  Serial.println("          elbow/gripper");
  Serial.println("+ / -   = jog 1 degree");
  Serial.println("] / [   = jog 5 degrees");
  Serial.println("c       = print current pose");
  Serial.println("---------------------------");
  Serial.println("? = Show this menu");
  Serial.println("===========================");
}

// ======================================================
// SETUP
// ======================================================

void setup() {
  Serial.begin(115200);

  delay(1000);

  // Hobby servos normally use 50 Hz control
  for (int j = 0; j < JOINT_COUNT; j++) {
    servos[j].setPeriodHertz(50);
  }

  // Wake the servos up one at a time so they do not all
  // jerk to HOME and draw current together.
  for (int j = 0; j < JOINT_COUNT; j++) {
    servos[j].attach(CONFIG[j].pin, SERVO_MIN_US, SERVO_MAX_US);
    writeJoint(j, getAngle(HOME, j));
    delay(300);
  }

  currentPose = constrainPose(HOME);

  delay(700);

  Serial.println();
  Serial.println("Robot arm ready!");

  printMenu();
}

// ======================================================
// LOOP
// ======================================================

void loop() {
  if (!Serial.available()) {
    return;
  }

  char command = Serial.read();

  switch (command) {
    case 'h':
    case 'H':
      Serial.println("Going HOME");
      moveTo(HOME, 1000);
      break;

    case 't':
    case 'T':
      testServos();
      break;

    case 'p':
    case 'P':
      pickAndPlace();
      break;

    case 'x':
    case 'X':
      Serial.println("Nothing is moving");
      break;

    case 'b':
    case 'B':
      selectJoint(BASE);
      break;

    case 's':
    case 'S':
      selectJoint(SHOULDER);
      break;

    case 'e':
    case 'E':
      selectJoint(ELBOW);
      break;

    case 'g':
    case 'G':
      selectJoint(GRIPPER);
      break;

    case '+':
    case '=':
      jog(1);
      break;

    case '-':
    case '_':
      jog(-1);
      break;

    case ']':
      jog(5);
      break;

    case '[':
      jog(-5);
      break;

    case 'c':
    case 'C':
      printPose();
      break;

    case '?':
      printMenu();
      break;

    case '\r':
    case '\n':
      // Ignore line endings sent when Enter is pressed.
      break;

    default:
      Serial.print("Unknown command: ");
      Serial.println(command);
      Serial.println("Type ? to show the menu.");
      break;
  }
}
