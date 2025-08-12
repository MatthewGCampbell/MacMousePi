# Macintosh 512K USB Mouse Adapter (or any Macintosh with DB‑9)

This project lets a modern USB mouse connected to a Raspberry Pi control a vintage Macintosh (e.g., 512K) through its original DB‑9 mouse port.

It supports **two modes**:

1. **Raspberry Pi Zero Only** — Pi reads the mouse and directly generates quadrature signals (no Arduino).
2. **Raspberry Pi + Arduino** — Pi reads the mouse and sends serial commands to an Arduino, which outputs quadrature.

---

## Hardware Overview

- **Raspberry Pi (any model with USB)**
  - Reads a USB mouse using Python (`evdev`).
  - Either:
    - Outputs quadrature directly to the DB‑9 (**Pi Zero only mode**), or
    - Sends serial commands to an Arduino (**Pi + Arduino mode**).

- **Arduino (5V logic, *Pi + Arduino mode only*)**
  - Receives serial commands from Pi.
  - Generates quadrature signals (X1/X2, Y1/Y2) to emulate a Macintosh mouse.

---

## Wiring

### 1) Raspberry Pi Zero → DB‑9 (Pi Zero Only Mode)

| DB‑9 Pin | Pi GPIO | Signal | Description               |
|----------|---------|--------|---------------------------|
| 4        | GPIO17  | X1     | Quadrature X phase 1      |
| 5        | GPIO27  | X2     | Quadrature X phase 2      |
| 8        | GPIO22  | Y1     | Quadrature Y phase 1      |
| 9        | GPIO23  | Y2     | Quadrature Y phase 2      |
| 7        | GPIO24  | BTN    | Mouse button (active low) |
| 1 & 3    | GND     | GND    | Ground                    |

> ⚠️ The Mac expects ~5V logic. Many builds work directly from the Pi’s 3.3V, but for best margins use a 74HCT buffer or transistor level shifting.

---

### 2) Raspberry Pi → Arduino (Serial, Pi + Arduino Mode)

| Raspberry Pi GPIO | Arduino Pin | Description   |
|-------------------|-------------|---------------|
| GPIO14 (TX)       | RX (Pin 0)  | Pi → Arduino  |
| GND               | GND         | Common ground |

> ⚠️ If you ever wire Arduino TX → Pi RX, **use a level shifter** to protect the Pi.

---

### 3) Arduino → DB‑9 (Macintosh Mouse Port)

| DB‑9 Pin | Arduino Pin | Signal | Description               |
|----------|-------------|--------|---------------------------|
| 4        | X1 GPIO     | X1     | Quadrature X phase 1      |
| 5        | X2 GPIO     | X2     | Quadrature X phase 2      |
| 8        | Y1 GPIO     | Y1     | Quadrature Y phase 1      |
| 9        | Y2 GPIO     | Y2     | Quadrature Y phase 2      |
| 7        | Button GPIO | BTN    | Mouse button (active low) |
| 1 & 3    | GND         | GND    | Ground                    |

---

## Software Overview

- **Pi Zero Only Mode**
  - Script: `just-the-pi/pi_mouse_direct.py`
  - Uses `evdev` (mouse input) + `RPi.GPIO` (quadrature outputs).

- **Pi + Arduino Mode**
  - Pi script: `mouse_to_serial.py` (reads mouse, sends serial commands).
  - Arduino sketch: `arduino-code.ino` (parses commands, generates quadrature).

---

## Project Files

- `arduino-code.ino` — Arduino sketch (only for Pi + Arduino mode)
- `mouse_to_serial.py` — Pi → Arduino bridge (Pi + Arduino mode)
- `just-the-pi/pi_mouse_direct.py` — **Pi Zero only** direct quadrature driver

---

## Pi Zero Only Setup

1. **Install Python environment**
   ```bash
   sudo apt update
   sudo apt install -y python3-venv python3-pip
   python3 -m venv ~/macmouse-venv
   source ~/macmouse-venv/bin/activate
   pip install evdev RPi.GPIO
