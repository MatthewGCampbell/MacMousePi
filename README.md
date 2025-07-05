# Macintosh 512K USB Mouse Adapter

This project allows a modern USB mouse connected to a Raspberry Pi to control a vintage Macintosh 512K through its original DB-9 mouse port. It uses a Raspberry Pi to read USB mouse movements and send them via serial to an Arduino R4 Minima, which outputs the quadrature signals required by the Mac's mouse interface.

---

## Hardware Overview

- **Raspberry Pi (any model with USB)**
  - Reads a modern USB mouse using Python (`evdev` library).
  - Converts mouse movement/button events to serial commands.
  - Sends commands over TX pin to Arduino.

- **Arduino UNO R4 Minima**
  - Receives serial commands on its RX pin.
  - Generates quadrature signals (X1/X2, Y1/Y2) to emulate a Macintosh mouse.
  - Outputs signals on GPIO pins connected to a DE-9 (DB-9) connector.
  - Connects to the Mac’s mouse port with a DB-9 cable.

---

## Wiring

### 1️⃣ Raspberry Pi → Arduino R4 Minima (Serial)
| Raspberry Pi GPIO | Arduino R4 Pin | Description      |
|-------------------|----------------|------------------|
| GPIO14 (TX)       | RX (Pin 0)     | Pi sends data    |
| GND               | GND            | Common ground    |

> ⚠️ **Important:** The Arduino R4 Minima uses 5V logic, and the Raspberry Pi uses 3.3V logic. In most cases, the Pi’s TX → Arduino RX is fine because the Arduino reads 3.3V as high. But if adding Arduino TX → Pi RX later, a level shifter **must** be used to avoid damaging the Pi.

---

### 2️⃣ Arduino → DB-9 Connector (Macintosh Mouse Port)
| DB-9 Pin | Arduino Pin | Signal    | Description             |
|----------|-------------|-----------|-------------------------|
| 4        | X1 GPIO     | X1        | Quadrature X phase 1    |
| 5        | X2 GPIO     | X2        | Quadrature X phase 2    |
| 8        | Y1 GPIO     | Y1        | Quadrature Y phase 1    |
| 9        | Y2 GPIO     | Y2        | Quadrature Y phase 2    |
| 7        | Button GPIO | BTN       | Mouse button (active low) |
| 1 & 3    | GND         | GND       | Ground connections      |

---

## Software Overview

### On the Raspberry Pi
- Python script (`mouse_to_serial.py`) running inside your virtual environment `macmouse-venv`.
- Uses `evdev` to read USB mouse events.
- Sends movement (`X:value\n` / `Y:value\n`) and button (`BTN:0/1\n`) commands over serial.

### On the Arduino
- Sketch reads serial input from the Pi.
- Parses commands like `X:5\n` or `BTN:1\n`.
- Updates quadrature waveform outputs accordingly to simulate mouse movements and button clicks.
- Outputs correct signal timing for the Mac’s mouse controller.

---

## Running the System

1. **Power the Raspberry Pi** and connect the USB mouse.
2. **Connect Pi TX → Arduino RX** and common ground.
3. **Connect the Arduino’s DB-9 connector to the Mac’s mouse port.**
4. On the Raspberry Pi, start your script (already configured for autostart if you used a systemd service):
   ```bash
   source ~/macmouse-venv/bin/activate
   python ~/mouse_to_serial.py
