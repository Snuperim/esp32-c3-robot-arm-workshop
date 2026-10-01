#include <Arduino.h>
#include <ESP32Servo.h>

// ======================================================
// ROBOT ARM - ESP32-C3
// Base + Shoulder + Elbow + Gripper
// ======================================================

// -------------------- SERVOS ---------------------------

Servo baseServo;
Servo shoulderServo;
Servo elbowServo;
Servo gripperServo;

// -------------------- GPIO PINS ------------------------

const int BASE_PIN     = 3;
const int SHOULDER_PIN = 4;
const int ELBOW_PIN    = 5;
const int GRIPPER_PIN  = 6;

// -------------------- SAFE LIMITS ----------------------
// THESE ARE STARTING VALUES ONLY.
//
// Calibrate these on the real robot before using the
// automatic sequence.

const int BASE_MIN     = 20;
const int BASE_MAX     = 160;

const int SHOULDER_MIN = 30;
const int SHOULDER_MAX = 150;

const int ELBOW_MIN    = 30;
const int ELBOW_MAX    = 150;

const int GRIPPER_MIN  = 20;
const int GRIPPER_MAX  = 90;

// -------------------- ROBOT POSE -----------------------

struct Pose {
  int base;
  int shoulder;
  int elbow;
  int gripper;
};

// -------------------- CURRENT POSITION ----------------

Pose currentPose = {
  90,   // base
  90,   // shoulder
  90,   // elbow
  30    // gripper
};

// ======================================================
// PREDEFINED ROBOT POSITIONS
// ======================================================

// Neutral safe position
const Pose HOME = {
  90,
  90,
  90,
  30
};

// Arm positioned above pickup object
const Pose PICK_APPROACH = {
  45,
  95,
  80,
  30
};

// Arm lowered toward object
const Pose PICK = {
  45,
  120,
  60,
  30
};

// Object gripped
const Pose GRAB = {
  45,
  120,
  60,
  75
};

// Raise object
const Pose LIFT = {
  45,
  80,
  90,
  75
};

// Position above drop zone
const Pose PLACE_APPROACH = {
  135,
  85,
  90,
  75
};

// Lower into drop position
const Pose PLACE = {
  135,
  115,
  65,
  75
};

// Release object
const Pose RELEASE = {
  135,
  115,
  65,
  30
};

// ======================================================
// LIMIT FUNCTION
// ======================================================

Pose constrainPose(Pose p) {

  p.base =
      constrain(p.base, BASE_MIN, BASE_MAX);

  p.shoulder =
      constrain(p.shoulder, SHOULDER_MIN, SHOULDER_MAX);

  p.elbow =
      constrain(p.elbow, ELBOW_MIN, ELBOW_MAX);

  p.gripper =
      constrain(p.gripper, GRIPPER_MIN, GRIPPER_MAX);

  return p;
}

// ======================================================
// WRITE POSE
// ======================================================

void writePose(Pose p) {

  p = constrainPose(p);

  baseServo.write(p.base);
  shoulderServo.write(p.shoulder);
  elbowServo.write(p.elbow);
  gripperServo.write(p.gripper);

  currentPose = p;
}

// ======================================================
// SMOOTH MOVEMENT
// ======================================================

void moveTo(Pose target, int durationMs) {

  target = constrainPose(target);

  Pose start = currentPose;

  const int steps = 50;

  for (int i = 1; i <= steps; i++) {

    float progress =
        (float)i / (float)steps;

    Pose intermediate;

    intermediate.base =
        start.base +
        (target.base - start.base) * progress;

    intermediate.shoulder =
        start.shoulder +
        (target.shoulder - start.shoulder) * progress;

    intermediate.elbow =
        start.elbow +
        (target.elbow - start.elbow) * progress;

    intermediate.gripper =
        start.gripper +
        (target.gripper - start.gripper) * progress;

    writePose(intermediate);

    delay(durationMs / steps);
  }

  currentPose = target;
}

// ======================================================
// PICK AND PLACE SEQUENCE
// ======================================================

void pickAndPlace() {

  Serial.println("Starting pick and place");

  // HOME
  moveTo(HOME, 1000);
  delay(500);

  // Move toward object
  moveTo(PICK_APPROACH, 1000);
  delay(300);

  // Lower arm
  moveTo(PICK, 800);
  delay(300);

  // Close gripper
  moveTo(GRAB, 500);
  delay(500);

  // Lift object
  moveTo(LIFT, 1000);
  delay(300);

  // Rotate toward target
  moveTo(PLACE_APPROACH, 1200);
  delay(300);

  // Lower object
  moveTo(PLACE, 800);
  delay(300);

  // Open gripper
  moveTo(RELEASE, 500);
  delay(500);

  // Move away from target
  moveTo(PLACE_APPROACH, 800);

  // Return HOME
  moveTo(HOME, 1200);

  Serial.println("Sequence complete");
}

// ======================================================
// SERVO TEST
// ======================================================

void testServos() {

  Serial.println("Testing base");
  baseServo.write(70);
  delay(800);
  baseServo.write(110);
  delay(800);
  baseServo.write(90);

  Serial.println("Testing shoulder");
  shoulderServo.write(70);
  delay(800);
  shoulderServo.write(110);
  delay(800);
  shoulderServo.write(90);

  Serial.println("Testing elbow");
  elbowServo.write(70);
  delay(800);
  elbowServo.write(110);
  delay(800);
  elbowServo.write(90);

  Serial.println("Testing gripper");
  gripperServo.write(30);
  delay(800);
  gripperServo.write(70);
  delay(800);
  gripperServo.write(30);

  writePose(HOME);

  Serial.println("Test complete");
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
  baseServo.setPeriodHertz(50);
  shoulderServo.setPeriodHertz(50);
  elbowServo.setPeriodHertz(50);
  gripperServo.setPeriodHertz(50);

  // Attach servos
  //
  // Starting conservatively with 1000-2000 us.
  // Adjust only after testing the actual servos.

  baseServo.attach(
      BASE_PIN,
      1000,
      2000
  );

  shoulderServo.attach(
      SHOULDER_PIN,
      1000,
      2000
  );

  elbowServo.attach(
      ELBOW_PIN,
      1000,
      2000
  );

  gripperServo.attach(
      GRIPPER_PIN,
      1000,
      2000
  );

  // Start robot in HOME position
  writePose(HOME);

  delay(1000);

  Serial.println();
  Serial.println("Robot arm ready!");

  printMenu();
}

// ======================================================
// LOOP
// ======================================================

void loop() {

  if (Serial.available()) {

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
}
