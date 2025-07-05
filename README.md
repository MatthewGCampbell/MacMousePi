# Macintosh 512K USB Mouse Adapter (Or any macintosh with db9)

This project allows a modern USB mouse connected to a Raspberry Pi to control a vintage Macintosh 512K through its original DB-9 mouse port. It uses a Raspberry Pi to read USB mouse movements and send them via serial to an Arduino (with 5V logic), which outputs the quadrature signals required by the Mac's mouse interface.

---

## Hardware Overview

- **Raspberry Pi (any model with USB)**
  - Reads a modern USB mouse using Python (`evdev` library).
  - Converts mouse movement/button events to serial commands.
  - Sends commands over TX pin to the Arduino.

- **Arduino (any model with 5V logic)**
  - Receives serial commands on its RX pin.
  - Generates quadrature signals (X1/X2, Y1/Y2) to emulate a Macintosh mouse.
  - Outputs signals on GPIO pins connected to a DE-9 (DB-9) connector.
  - Connects to the Mac’s mouse port with a DB-9 cable.

---

## Wiring

### 1️⃣ Raspberry Pi → Arduino (Serial)
| Raspberry Pi GPIO | Arduino Pin | Description      |
|-------------------|-------------|------------------|
| GPIO14 (TX)       | RX (Pin 0)  | Pi sends data    |
| GND               | GND         | Common ground    |

> ⚠️ **Important:** The Arduino uses 5V logic, and the Raspberry Pi uses 3.3V logic. In most cases, the Pi’s TX → Arduino RX is fine because the Arduino reads 3.3V as high. But if adding Arduino TX → Pi RX later, a level shifter **must** be used to avoid damaging the Pi.

---

### 2️⃣ Arduino → DB-9 Connector (Macintosh Mouse Port)
| DB-9 Pin | Arduino Pin | Signal    | Description               |
|----------|-------------|-----------|---------------------------|
| 4        | X1 GPIO     | X1        | Quadrature X phase 1      |
| 5        | X2 GPIO     | X2        | Quadrature X phase 2      |
| 8        | Y1 GPIO     | Y1        | Quadrature Y phase 1      |
| 9        | Y2 GPIO     | Y2        | Quadrature Y phase 2      |
| 7        | Button GPIO | BTN       | Mouse button (active low) |
| 1 & 3    | GND         | GND       | Ground connections        |

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

## Project Files

This project uses two main files:

- **arduino-code.ino**  
  Arduino sketch for any compatible Arduino board with 5V logic.
  - Upload this file to your Arduino using the Arduino IDE or `arduino-cli`.
  - This sketch reads serial commands from the Raspberry Pi and generates the quadrature outputs for the Mac.

- **mouse_to_serial.py**  
  Python script for the Raspberry Pi.
  - Make sure you’ve set up your virtual environment (`macmouse-venv`) with `evdev` and `pyserial` installed:
    ```bash
    python3 -m venv ~/macmouse-venv
    source ~/macmouse-venv/bin/activate
    pip install evdev pyserial
    ```
  - Run the script manually with:
    ```bash
    source ~/macmouse-venv/bin/activate
    python ~/mouse_to_serial.py
    ```
  - Or enable the systemd service you created for autostart on boot.

---

## Setup Steps

1. **Prepare the Raspberry Pi:**
   - Install Python virtual environment as shown above.
   - Copy `mouse_to_serial.py` to your home directory (e.g., `/home/pi/mouse_to_serial.py`).

2. **Prepare the Arduino:**
   - Connect your Arduino to your computer via USB.
   - Open `arduino-code.ino` in the Arduino IDE.
   - Select the correct board type (e.g., Arduino Uno, Nano) and port.
   - Upload the sketch.

3. **Connect the Hardware:**
   - Wire Raspberry Pi TX → Arduino RX, and connect GND.
   - Wire Arduino outputs to the DB-9 connector as described earlier.

4. **Run the System:**
   - Boot the Raspberry Pi. The systemd service will launch `mouse_to_serial.py` automatically if you set it up, or you can run it manually:
     ```bash
     source ~/macmouse-venv/bin/activate
     python ~/mouse_to_serial.py
     ```
   - Move your USB mouse, and watch the Macintosh 512K respond with accurate cursor movement and clicks.

---

## Notes

- Make sure the baud rate in both `mouse_to_serial.py` and `arduino-code.ino` match (default: 115200).
- You can adjust thresholds or debounce times by editing `mouse_to_serial.py`.

---

## License

MIT License. See `LICENSE` file for details.

---

## Acknowledgements

- Original Macintosh mouse protocol reverse-engineered from Apple hardware documentation.
- Inspired by various vintage computing communities and USB-to-quadrature projects.
