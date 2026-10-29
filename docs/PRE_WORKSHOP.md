# Pre-Workshop Setup

Do this at home, before the workshop. Plan on 45 to 60 minutes. Most of that time is downloading, not typing.

You need three tools: **Visual Studio Code**, **PlatformIO** (it builds the firmware) and **Wokwi** (it runs the arm's circuit on your screen, no hardware needed). You also need a **GitHub** account, because the workshop includes a short version-control part, and an **AI assistant** that your facilitator approves. When you finish, you will have run the virtual arm on your own computer and pushed a branch to your own copy of the project. **Webots**, a 3D simulator, is optional.

At the end of each step there is a **Check**. If a check fails, fix it before you move on, because the next step depends on it.

## Before you begin

- A Windows or Mac laptop that you can install software on. Some installers need an administrator password.
- About 3 GB of free disk space. The first build downloads the ESP32 toolchain and framework, which together take well over 1 GB once unpacked.
- A good internet connection for the first build.
- A free Wokwi account (you create it in Step 5) and a free GitHub account (you create it in Step 6).

You do not need the physical arm or the ESP32 board for any required step.

## Step 1: Install Visual Studio Code

Download it from [code.visualstudio.com](https://code.visualstudio.com/) and install it with the default options.

**Check:** VS Code opens.

## Step 2: Install Git

PlatformIO uses Git to fetch some packages, and you will use it to download the project.

- **Windows:** install Git from [git-scm.com](https://git-scm.com/).
- **Mac:** open the Terminal and run `git --version`. If Git is missing, macOS offers to install the command line tools. Accept.

**Check:** in a terminal, `git --version` prints a version number.

## Step 3: Install PlatformIO

1. In VS Code, open the Extensions view. The shortcut is Ctrl+Shift+X on Windows and Cmd+Shift+X on Mac.
2. Search for `PlatformIO IDE` and install the official extension.
3. Wait until the status bar finishes installing PlatformIO Core. When VS Code asks, reload the window.

**Check:** the PlatformIO icon appears in the left sidebar, and PlatformIO Home opens.

## Step 4: Install the Wokwi extension

In the Extensions view, search for `Wokwi for VS Code` and install it.

**Check:** the extension shows as installed. It will not run until you activate the licence in Step 5.

## Step 5: Activate your free Wokwi licence

1. Press `F1` to open the command palette. (Ctrl+Shift+P on Windows or Cmd+Shift+P on Mac also works.)
2. Run **Wokwi: Request a new License**.
3. When VS Code asks to open the Wokwi website, confirm.
4. On the website, click **GET YOUR LICENSE** and sign in. If you have no account, create one. Wokwi says an account is free.
5. Confirm sending the licence back to VS Code. You may need to confirm in both the browser and VS Code.

If Wokwi shows a price or a limit that stops you, tell your facilitator before the workshop.

**Check:** VS Code shows the message `License activated for` followed by your name.

## Step 6: Create a GitHub account and set up Git

1. Create a free account at [github.com](https://github.com/) if you do not have one. In **Settings, Emails** you can choose to keep your email address private. GitHub then gives you a no-reply address to use for your commits.
2. In a terminal, tell Git who you are:

```text
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

Use the no-reply address from GitHub if you chose to keep your email private.

**Check:** `git config --global --list` shows your name and email, and you can sign in at github.com.

## Step 7: Get the project

1. Open the project page: [github.com/Snuperim/esp32-c3-robot-arm-workshop](https://github.com/Snuperim/esp32-c3-robot-arm-workshop). Choose **Fork**, then **Create fork**. This makes your own copy, where you are allowed to push changes.
2. In a terminal, clone your copy. Replace `your-username` with your GitHub name:

```text
git clone https://github.com/your-username/esp32-c3-robot-arm-workshop.git
```

If you prefer not to use Git, choose **Code**, then **Download ZIP** on the project page and unzip the file. That is enough for the build and the simulation, but you will not be able to push your changes.

In VS Code, choose **File, Open Folder** and select the folder that contains `platformio.ini`. Do not open a folder inside it, such as `src`.

**Check:** the Explorer shows `platformio.ini`, `diagram.json`, `wokwi.toml` and a `src` folder at the top level.

## Step 8: Build the firmware

1. Open the PlatformIO sidebar and go to **Project Tasks, wokwi, General, Build**. You can also run **PlatformIO: Build** from the command palette.
2. Wait. The first build downloads the toolchain and the framework, so it can take several minutes. Later builds take seconds.

**Check:** the terminal ends with `SUCCESS`, and this file exists: `.pio/build/wokwi/firmware.bin`.

## Step 9: Run the virtual arm

1. Open `diagram.json`.
2. Press `F1` and run **Wokwi: Start Simulator**.
3. Click inside the terminal that is built into the Wokwi window. Type `?` and press Enter to see the menu.
4. Type `t` and press Enter.

**Check:** all four virtual servos move.

Take a screenshot of the Wokwi window showing the menu and send it to your facilitator. That is how they know you are ready.

If the simulator reports `firmware.bin not found`, go back to Step 8.

## Step 10: Check that you can push to GitHub

Run these commands in the VS Code terminal (Terminal, New Terminal), inside the project folder:

```text
git switch -c my-arm
git commit --allow-empty -m "Start my arm branch"
git push -u origin my-arm
```

The first push should open a browser window to sign in. GitHub does not accept your account password for Git over HTTPS, so use that browser sign-in. If no sign-in appears, another way is the GitHub command line tool: install it and run `gh auth login`. If neither works, tell your facilitator.

**Check:** your fork on github.com lists a branch called `my-arm`.

## Step 11: Choose your AI assistant

Your facilitator will tell you which assistants the workshop allows. Create an account if you need one, because free plans differ between tools. Then read [AI_WORKFLOW.md](AI_WORKFLOW.md) once. It explains how to use an assistant for debugging, for Git and for starting a project, and it lists the rules for this workshop.

**Check:** you can open a chat with your assistant and paste in a short error message. Never paste passwords or tokens.

## Optional A: Webots (3D simulator)

Webots is not needed for the workshop. It is a bonus for anyone who wants to see the arm in 3D.

1. Download Webots R2025a from [cyberbotics.com](https://cyberbotics.com/) and install it. The project was built with that version, and other versions are untested.
2. **Windows:** in VS Code, run **Terminal, Run Task, Webots: Open robot arm**. The installation guide in [SETUP_GUIDE.md](SETUP_GUIDE.md) lists the path the launcher expects.
3. **Mac:** the launcher script is Windows only. Open the Webots app, choose **File, Open World**, and select `webots/worlds/robot_arm.wbt` from the project folder.
4. Start the simulation, click the 3D view, and press `P`.

If Webots reports a problem with Python, look for the Python command in Webots Preferences. The Webots documentation explains this for your version.

**Check:** the grey arm appears, and `P` makes it move.

## Optional B: The ESP32-C3 board

Only do this if you already have the board. Do not connect any servo.

1. Plug the board into your computer with a USB cable.
2. In PlatformIO, open **PIO Home, Devices**.

**Check:** a serial port appears when you plug the board in and disappears when you unplug it.

If no port appears, the board's USB-to-serial chip may need a driver. Many boards use a CP210x or CH340 chip. Look up the chip name printed on the board and install its driver.

## Windows and Mac

Steps 1 to 11 are the same on both systems. Only the shortcut keys differ. This project has been tested on Windows only. If a step behaves differently on your Mac, write down what you saw and tell your facilitator.

## If something goes wrong

| What you see | What to try |
| --- | --- |
| PlatformIO cannot install packages from the VS Code terminal | Run the same command from a system terminal, then return to VS Code. |
| The first build fails with a download or connection error | Check your internet connection. On a school or company network, set the proxy in VS Code and try again. |
| `firmware.bin not found` in Wokwi | Build the project again (Step 8), then restart the simulator. |
| You changed the code and Wokwi shows the old behaviour | Build again, stop the simulator and start it again. |
| Webots shows a blank 3D view on Windows | See the Webots problems section in [SETUP_GUIDE.md](SETUP_GUIDE.md). |

More fixes are in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## You are ready when

- [ ] VS Code, Git and PlatformIO are installed.
- [ ] Your Wokwi licence is active.
- [ ] You have a GitHub account, and Git knows your name and email.
- [ ] The project folder is open and the build ends in `SUCCESS`.
- [ ] Typing `t` in the Wokwi terminal moves four virtual servos.
- [ ] Your fork on GitHub shows the `my-arm` branch.
- [ ] You have chosen your AI assistant and read the AI guide.
- [ ] You sent your facilitator the screenshot.

Then continue with the [Workshop Guide](WORKSHOP_GUIDE.md).
