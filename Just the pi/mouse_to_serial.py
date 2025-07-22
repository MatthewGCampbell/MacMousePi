#!/usr/bin/env python3
import evdev
import RPi.GPIO as GPIO
import time
import fcntl, os, select

# GPIO pins for quadrature outputs (BCM numbering)
X1, X2 = 6, 5
Y1, Y2 = 4, 3
BTN = 2

# Quadrature waveform phases matching waveform1/waveform2
waveform = [
    (1, 1),  # idx 0: HIGH, HIGH
    (0, 1),  # idx 1: LOW,  HIGH
    (0, 0),  # idx 2: LOW,  LOW
    (1, 0),  # idx 3: HIGH, LOW
]

GPIO.setmode(GPIO.BCM)
GPIO.setup([X1, X2, Y1, Y2, BTN], GPIO.OUT, initial=GPIO.HIGH)

x_idx, y_idx = 0, 0
x_pending, y_pending = 0, 0

def write_quadrature_axis(axis, idx):
    if axis == 'x':
        GPIO.output(X1, waveform[idx % 4][0])
        GPIO.output(X2, waveform[idx % 4][1])
    else:
        GPIO.output(Y1, waveform[idx % 4][0])
        GPIO.output(Y2, waveform[idx % 4][1])

def scale_delta(delta):
    abs_delta = abs(delta)
    sign = 1 if delta > 0 else -1
    if abs_delta < 4:
        scaled = abs_delta
    elif abs_delta < 12:
        scaled = int(abs_delta * 2)
    elif abs_delta < 35:
        scaled = abs_delta * 4
    else:
        scaled = abs_delta * 6
    # Clamp scaled delta to avoid huge pending spikes causing jitter
    return max(-50, min(50, sign * scaled))

def handle_button(ev):
    GPIO.output(BTN, GPIO.LOW if ev.value else GPIO.HIGH)

# Find USB mouse device
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
mouse = None
for d in devices:
    if 'mouse' in d.name.lower():
        mouse = d
        break
if not mouse:
    print("No USB mouse found. Plug one in and try again.")
    exit(1)

print(f"Using USB mouse: {mouse.name} at {mouse.path}")
mouse.grab()

# Make mouse device non-blocking
flags = fcntl.fcntl(mouse.fd, fcntl.F_GETFL)
fcntl.fcntl(mouse.fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

write_quadrature_axis('x', x_idx)
write_quadrature_axis('y', y_idx)
GPIO.output(BTN, GPIO.HIGH)

try:
    while True:
        max_pending = max(abs(x_pending), abs(y_pending))

        # Truncate pending buffers to avoid infinite lag
        max_queue = 300
        if abs(x_pending) > max_queue:
            x_pending = max_queue if x_pending > 0 else -max_queue
        if abs(y_pending) > max_queue:
            y_pending = max_queue if y_pending > 0 else -max_queue

        # Softer dynamic feeding to avoid overshooting
        if max_pending > 200:
            steps_per_loop = 8     # was 16
            delay = 0.00003
        elif max_pending > 100:
            steps_per_loop = 4     # was 8
            delay = 0.00005
        elif max_pending > 50:
            steps_per_loop = 2     # was 4
            delay = 0.00008
        else:
            steps_per_loop = 1
            delay = 0.00012  # Arduino-like timing

        did_step = False

        # Feed X pending
        for _ in range(steps_per_loop):
            if x_pending != 0:
                dir = 1 if x_pending > 0 else -1
                x_idx = (x_idx + dir) % 4
                write_quadrature_axis('x', x_idx)
                x_pending -= dir
                did_step = True

        # Feed Y pending
        for _ in range(steps_per_loop):
            if y_pending != 0:
                dir = 1 if y_pending > 0 else -1
                y_idx = (y_idx + dir) % 4
                write_quadrature_axis('y', y_idx)
                y_pending -= dir
                did_step = True

        if did_step:
            time.sleep(delay)
        else:
            # If no pending steps, check for mouse events
            rlist, _, _ = select.select([mouse.fd], [], [], 0)
            if rlist:
                for event in mouse.read():
                    if event.type == evdev.ecodes.EV_REL:
                        if event.code == evdev.ecodes.REL_X:
                            if abs(event.value) >= 2:  # deadzone: ignore small jitters
                                x_pending += scale_delta(event.value)
                        elif event.code == evdev.ecodes.REL_Y:
                            if abs(event.value) >= 2:
                                y_pending += scale_delta(-event.value)
                    elif event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.BTN_LEFT:
                        handle_button(event)

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    mouse.ungrab()
    GPIO.cleanup()