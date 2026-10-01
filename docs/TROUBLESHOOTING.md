# Troubleshooting

## Recommended simulation workflow

For workshop participants, use Wokwi's **built-in terminal** first:

1. Run **PlatformIO: Build**.
2. Confirm `.pio/build/wokwi/firmware.bin` exists.
3. Open `diagram.json`.
4. Start Wokwi.
5. Use the terminal inside the Wokwi simulator.
6. Type `?` or `t` and press Enter.

A physical COM port is not required for Wokwi simulation.

## `firmware.bin` not found

The default PlatformIO environment is `wokwi`. Build the project and confirm:

```text
.pio/build/wokwi/firmware.bin
```

If the file is missing, check that `platformio.ini` still contains the `[env:wokwi]` environment and that `wokwi.toml` points to `.pio/build/wokwi/firmware.bin`.

## Wokwi starts with old firmware

Wokwi loads the compiled binary named in `wokwi.toml` when the simulation starts.

1. Stop the simulator.
2. Run **PlatformIO: Build**.
3. Start Wokwi again.

Changing `src/main.cpp` without rebuilding does not update the simulated firmware.

## Wokwi terminal is empty

1. Confirm **PlatformIO: Build** succeeds.
2. Confirm the simulator is running rather than paused.
3. Type `?` and press Enter.
4. Stop and restart Wokwi if necessary.
5. Reopen `diagram.json` if you recently changed the virtual wiring.

The terminal is configured in `diagram.json` with `"display": "terminal"`.

## Servos do not move in Wokwi

Run `t` and check whether servo-test messages appear in the terminal.

If messages appear but the virtual servos do not move, verify the signal wiring in `diagram.json`:

```text
GPIO3 → Base
GPIO4 → Shoulder
GPIO5 → Elbow
GPIO6 → Gripper
```

Also confirm each virtual servo has a 5 V and GND connection.

## Optional PlatformIO Serial Monitor

The external PlatformIO Serial Monitor is optional. The built-in Wokwi terminal is simpler for participants.

If you do want the PlatformIO monitor, the simulation must be running first. The complete serial-forwarding path is:

1. `wokwi.toml` enables `rfc2217ServerPort = 4000`.
2. the `wokwi` environment in `platformio.ini` uses `monitor_port = rfc2217://localhost:4000`.
3. `diagram.json` connects the simulated ESP32 UART:

```json
[ "esp:TX", "$serialMonitor:RX", "", [] ],
[ "esp:RX", "$serialMonitor:TX", "", [] ]
```

TX and RX are crossed because one side's transmitter connects to the other side's receiver.

After changing `diagram.json`, stop Wokwi and start the simulation again.

## PlatformIO Serial Monitor asks for a COM port

If you are trying to simulate in Wokwi, stop the monitor and start Wokwi instead. The recommended simulation workflow does not use a COM port.

If you are working with the **physical** robot, select the `physical` PlatformIO environment and then use the COM port assigned to the connected ESP32-C3.

## Typed text appears in PlatformIO monitor but commands do nothing

Visible text may be local echo rather than data reaching the simulated ESP32.

Check that:

- Wokwi is running;
- the monitor header shows `rfc2217://localhost:4000`;
- both `$serialMonitor` wiring entries are present in `diagram.json`; and
- you restarted Wokwi after changing the diagram.

## Port 4000 is unavailable

Another Wokwi session or program may already be using it. Choose a different unused port and change both locations:

```toml
# wokwi.toml
rfc2217ServerPort = 4001
```

```ini
; platformio.ini
monitor_port = rfc2217://localhost:4001
```

## Physical upload uses the wrong environment

The repository separates simulation and hardware:

```text
wokwi    → ESP32-C3-DevKitM-1 virtual board
physical → ESP32-C3-DevKitC-02 real board
```

For a real board, use **PlatformIO → Project Tasks → physical → Upload**.

## Physical servos jitter or reset the ESP32

This usually indicates an inadequate supply or a missing common ground. Use a regulated external 5 V supply sized for servo stall current. Connect its ground to ESP32 ground, but do not route the combined servo current through the ESP32 board.

## A physical joint hits a mechanical stop

Disconnect servo power immediately. Reduce that joint's range in `src/main.cpp`, reposition the horn if required, and retest without a load. Do not rely on the example angle limits for a different arm.

## Commands are delayed

Motion is intentionally blocking: the firmware finishes the current movement before reading the next command. This keeps the workshop code easy to follow. A state-machine implementation is required for interruption or emergency-stop behavior.
