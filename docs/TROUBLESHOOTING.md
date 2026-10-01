# Troubleshooting

## What was fixed during initial setup

The firmware built correctly, but PlatformIO initially had no serial path to the simulated ESP32-C3. The complete fix required three layers:

1. Wokwi serial forwarding was enabled with `rfc2217ServerPort = 4000` in `wokwi.toml`.
2. PlatformIO was pointed at `rfc2217://localhost:4000` in `platformio.ini`.
3. The ESP32-C3 UART was explicitly connected in `diagram.json`:

   ```json
   [ "esp:TX", "$serialMonitor:RX", "", [] ],
   [ "esp:RX", "$serialMonitor:TX", "", [] ]
   ```

TX and RX are crossed because one side's transmitter connects to the other side's receiver. Local echo was enabled so typed characters are visible, and `send_on_enter` makes PlatformIO send a completed command when Enter is pressed.

Changes to `diagram.json` do not update an already-running simulation reliably. Stop Wokwi, close and reopen the diagram, and start the simulator again after changing its wiring.

## PlatformIO monitor connects but prints nothing

1. Confirm that **PlatformIO: Build** succeeds.
2. Stop the current simulation and serial monitor.
3. Reopen `diagram.json` and start Wokwi.
4. Keep the Wokwi tab visible; the simulator may pause when hidden.
5. Open PlatformIO Serial Monitor only after Wokwi is running.
6. Restart the simulation while the monitor is connected to capture startup output.
7. Type `?` and press Enter.

The monitor header should show `rfc2217://localhost:4000` and 115200 baud.

## Typed text appears but commands do nothing

Visible input can come from local echo alone. Check that both `$serialMonitor` wiring entries are present in `diagram.json`, then fully restart Wokwi. Also confirm that the simulator is running rather than paused.

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

## Wokwi starts with old firmware

Stop the simulator, run **PlatformIO: Build**, and start it again. Wokwi loads the binary named in `wokwi.toml` when the simulation starts.

## Physical servos jitter or reset the ESP32

This usually indicates an inadequate supply or a missing common ground. Use a regulated external 5 V supply sized for servo stall current. Connect its ground to ESP32 ground, but do not route the combined servo current through the ESP32 board.

## A physical joint hits a mechanical stop

Disconnect servo power immediately. Reduce that joint's range in `src/main.cpp`, reposition the horn if required, and retest without a load. Do not rely on the example angle limits for a different arm.

## Commands are delayed

Motion is intentionally blocking: the firmware finishes the current movement before reading the next command. This keeps the workshop code easy to follow. A state-machine implementation is required for interruption or emergency-stop behavior.
