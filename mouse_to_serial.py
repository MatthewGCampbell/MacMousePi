import serial
import evdev
import sys
import time

SERIAL_PORT = '/dev/serial0'  # Or e.g., '/dev/ttyUSB0' for USB-serial
BAUDRATE = 115200

# Configurable thresholds
MIN_MOVEMENT_THRESHOLD = 2  # Ignore movements smaller than this
BUTTON_DEBOUNCE_MS = 50     # Minimum time between button state changes

def find_mouse():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for dev in devices:
        if 'mouse' in dev.name.lower() or 'pointer' in dev.name.lower():
            return dev
    print("Mouse not found", file=sys.stderr)
    sys.exit(1)

def main():
    mouse = find_mouse()
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    except serial.SerialException as e:
        print(f"Serial error: {e}", file=sys.stderr)
        sys.exit(1)

    last_button_state = None
    last_button_time = 0  # For debouncing

    try:
        for event in mouse.read_loop():
            if event.type == evdev.ecodes.EV_REL:
                if event.code == evdev.ecodes.REL_X and abs(event.value) >= MIN_MOVEMENT_THRESHOLD:
                    cmd = f"X:{event.value}\n"
                    ser.write(cmd.encode())
                elif event.code == evdev.ecodes.REL_Y and abs(event.value) >= MIN_MOVEMENT_THRESHOLD:
                    cmd = f"Y:{event.value}\n"
                    ser.write(cmd.encode())
            elif event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.BTN_LEFT:
                now = time.time() * 1000  # Current time in ms
                if event.value != last_button_state and (now - last_button_time) > BUTTON_DEBOUNCE_MS:
                    cmd = f"BTN:{event.value}\n"
                    ser.write(cmd.encode())
                    last_button_state = event.value
                    last_button_time = now
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Runtime error: {e}", file=sys.stderr)
    finally:
        ser.close()

if __name__ == "__main__":
    main()
