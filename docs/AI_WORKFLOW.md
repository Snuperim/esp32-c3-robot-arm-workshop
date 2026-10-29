# Working With an AI Assistant

This guide shows how to use an AI assistant on this project in three ways: debugging, version control with Git and GitHub, and starting a new project. An assistant can save you time. It can also be confidently wrong, and on this project a wrong answer can mean a stalled servo. The habits below keep you in charge.

Your facilitator will tell you which assistant to use and what your institution allows.

## Ground rules

1. **You run it and you read it.** Do not accept code you cannot explain. If you cannot explain a line, ask the assistant to explain it, then check the explanation against the code.
2. **Hardware stays in your hands.** An assistant never powers or moves the arm. Switch servo power off before any wiring change, whatever the assistant suggested.
3. **No secrets in prompts.** Do not paste Wi-Fi passwords, access tokens, or personal data.
4. **Check facts at the source.** Pin numbers, library names and versions come from the datasheet, the PlatformIO registry and the project files, not from a chat.
5. **Say when AI helped.** If your course or your facilitator asks for it, add a short note such as `AI-assisted` to the commit message.

## Debugging with an assistant

A good question gets a good answer. Fill in this template and paste it in.

```text
Goal: what I expected to happen
Actual: what happened, with the exact error text or behaviour
Setup: board and PlatformIO environment (wokwi or physical), operating system
Code: the smallest part of the code that is involved
Tried: what I already changed or checked
Ask: list three likely causes and a quick way to test each one
```

Ask for causes and tests, not just a fix. A list of hypotheses lets you check each one yourself, and you learn why the problem happened.

Then follow this loop:

1. **Save a working state.** Commit before you experiment, so you can always go back.
2. **Test one hypothesis at a time.** If you change three things at once, you will not know which one mattered.
3. **Read what changed.** Run `git diff` to see exactly which lines the assistant's suggestion touched.
4. **Keep it or undo it.** If the change did not help, run `git restore <file>` to return the file to your last commit. This throws away uncommitted edits in that file, so use it only when you mean it.

Describe hardware in words. The assistant cannot see your wiring, your servo horns or your power supply. Ask it for a checklist, then work through the checklist yourself. Do not accept a verdict such as "your wiring is fine".

## Git and GitHub with an assistant

Git records the history of your project. GitHub stores a copy online and lets you share it. You need four commands for this workshop:

```text
git switch -c my-arm        make your own branch
git add src/main.cpp        choose what goes in the next commit
git commit -m "message"     save a snapshot with a message
git push -u origin my-arm   send the branch to your copy on GitHub
```

Run `git status` any time to see where you are.

**Where an assistant helps**

- **Commit messages.** Run `git diff --staged` to see what you are about to commit, ask the assistant to summarise it, then edit the result. A good message has a short first line in the imperative, such as `Set calibrated limits for my arm`.
- **Reading a diff.** Paste a diff and ask what it changes and what could break.
- **Merge conflicts.** When Git writes `<<<<<<<`, `=======` and `>>>>>>>` into a file, ask the assistant what each side means. You decide which lines stay.
- **Pull requests.** Ask for a description, then compare it with the real diff and fix anything it invented.

**What belongs in a commit.** Your calibrated limits and poses belong in a commit. Build output (`.pio`) is ignored by the repository, and secrets never belong in any commit.

**What the assistant cannot know.** Your calibration numbers come from your arm. Never let an assistant fill them in.

## Starting a new project with an assistant

1. **Describe the goal.** Give the board, the parts and what the project should do.
2. **Ask for a plan, not code.** Request a file layout, a wiring table and a list of libraries. Read the plan before anything is written.
3. **Verify every fact in the plan.**
   - Check each pin against the board's pinout and datasheet. On the ESP32-C3, look closely at GPIO 2, 8 and 9, which affect how the chip boots.
   - Search for each library on the PlatformIO registry and use the version it lists.
4. **Build early.** Get an almost empty project compiling, then add one feature at a time.
5. **Simulate first.** Test the circuit and code in Wokwi before you connect hardware.
6. **Commit after every step that works.**

An example first prompt:

```text
I want to build a project on an ESP32-C3 that reads a potentiometer and moves
one servo. I use PlatformIO and Wokwi. Give me a file layout, a wiring table
with pins, and the libraries I need. Do not write the code yet.
```

## Where assistants go wrong

- **Invented details.** They can name library functions or settings that do not exist, or give a pin that clashes with the board's boot behaviour.
- **Out-of-date advice.** Versions and menus change faster than the answers do.
- **Confident tone.** A wrong answer sounds as sure as a right one.
- **Wider edits than you asked for.** Always read the diff.
- **No view of your hardware.** They cannot see wiring, test a servo, or know your limits.

This project had three real examples:

- The first set of poses could not reach the table. A short calculation showed the arm's tip stayed well above it.
- A camera setting that looked fine in the file opened Webots with the arm out of frame. Only running it showed the problem.
- Webots kept rewriting the world file with its own saved state, and only reading the diff showed it before it was committed.

In each case, the fix came from checking, not from asking again.

## Checklist before you accept AI output

- [ ] I can explain every line.
- [ ] It builds without errors.
- [ ] I tested it in Wokwi before the real arm.
- [ ] The diff shows only what I asked for.
- [ ] There are no secrets in it.
- [ ] It keeps the joint limits in place (`constrainPose()` still clamps every angle).
- [ ] If it touches wiring or power, I switched the servo supply off first.

## Practice

1. Break something on purpose, such as a misspelled pin constant. Fill in the debugging template, ask for three causes, and test them one at a time.
2. Make a small change, run `git diff --staged`, ask for a commit message, and improve it.
3. Ask an assistant to add a `w` command that waves the arm. Compare its answer with the one in the workshop guide. What did it get right, and what did you have to fix?
4. Describe a project of your own and ask for a plan. Find at least one pin or library detail in it to check against a datasheet or registry.
