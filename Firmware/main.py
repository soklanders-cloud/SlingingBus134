import board
import busio
import digitalio
import time

import adafruit_ssd1306

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.matrix import DiodeOrientation
from kmk.modules.macros import Macros
from kmk.modules.new_encoder import EncoderHandler

keyboard = KMKKeyboard()

# -----------------------
# Hardware pin mapping
# -----------------------
# Columns (col0, col1, col2)
keyboard.col_pins = (board.GP1, board.GP2, board.GP4)

# Rows (row0, row1, row2)
keyboard.row_pins = (board.GP28, board.GP27, board.GP26)

keyboard.diode_orientation = DiodeOrientation.COL2ROW

# -----------------------
keyboard.keymap = [
    [
        KC.F1,    KC.UP,   KC.F3,   # row0 (up-left, up, up-right)
        KC.LEFT,  KC.SPACE,KC.RIGHT,# row1 (left, mid-stop, right)
        KC.F2,    KC.DOWN, KC.F4    # row2 (down-left, down, down-right)
    ]
]

# -----------------------
# Macros module (if you want to add string macros later)
# -----------------------
macros = Macros()


encoder_handler = EncoderHandler()
encoder_handler.pins = ((board.GP29, board.GP0, board.GP3, False),)
# map: (CCW, CW, BUTTON)
encoder_handler.map = (
    ((KC.KP_MINUS, KC.KP_PLUS, KC.ENTER),),  # Layer 0: speed down/up, press=enter
)

# ensure encoder button input has pull-up on GP3 (switch to GND)
btn_pin = digitalio.DigitalInOut(board.GP3)
btn_pin.direction = digitalio.Direction.INPUT
btn_pin.pull = digitalio.Pull.UP

# -----------------------
# OLED (0.91" typical - 128x32)
# SDA -> GP6, SCL -> GP7 (you said GP6= SDA, GP7 = SCL)
# -----------------------
OLED_WIDTH = 128
OLED_HEIGHT = 32  # most 0.91" modules are 32 tall

oled = None
try:
    # Note: busio.I2C expects (SCL, SDA) order on some ports; many Adafruit examples use I2C(SCL, SDA).
    i2c = busio.I2C(board.GP7, board.GP6)  # (SCL, SDA)
    # short attempt to initialize
    timeout = time.monotonic() + 1.0
    while not i2c.try_lock() and time.monotonic() < timeout:
        pass
    if i2c.locked:
        i2c.unlock()
    oled = adafruit_ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)
    oled.fill(0)
    oled.show()
except Exception as e:
    print("OLED init failed:", e)
    oled = None

# -----------------------
# Robot state & OLED helpers
# -----------------------
# state variables (updated when special keys pressed)
led_on = False
obstacle_avoid = False
follow_mode = False
speed = 50  # arbitrary speed value 0..100 shown on OLED
last_input = "None"

def current_mode_string():
    # precedence: Follow > Obstacle Avoid > Manual
    if follow_mode:
        return "Follow"
    if obstacle_avoid:
        return "Obstacle"
    return "Manual"

def oled_refresh():
    if not oled:
        return
    oled.fill(0)
    # top line: Mode and Speed
    oled.text("Mode:{:8}".format(current_mode_string()), 0, 0, 1)
    oled.text("Spd:{:3d}%".format(speed), 80, 0, 1)
    # second line: LED / Obstacle / Follow status (short)
    s = "LED:{} O:{:d} F:{:d}".format("On" if led_on else "Off", int(obstacle_avoid), int(follow_mode))
    oled.text(s, 0, 12, 1)
    # third line: last input (centered-ish)
    oled.text("Last:"+last_input[:18], 0, 22, 1)
    oled.show()

# initial OLED draw
oled_refresh()


# -----------------------
class RobotModule:
    """
    A small KMK module that watches key presses and updates
    internal robot state (led_on, obstacle_avoid, follow_mode, speed, last_input)
    and refreshes the OLED.

    NOTE: This uses the common KMK module hook `process_key` which
    many KMK versions call with (self, keyboard, key, is_pressed).
    If your KMK version has a different hook name, adapt accordingly.
    """
    def __init__(self):
        # nothing for now
        pass

    
    def process_key(self, keyboard_obj, key, is_pressed):
        # We only care about key-down events
        if not is_pressed:
            return

        global led_on, obstacle_avoid, follow_mode, speed, last_input

        # key is a KMK keycode constant (e.g., KC.F1). Compare with KC.* constants.
        if key == KC.F1:
            # toggle LED
            led_on = not led_on
            last_input = "LED On" if led_on else "LED Off"
        elif key == KC.F2:
            # open door (one-shot action)
            last_input = "Open Door"
            # (you could add additional behavior here, e.g. toggle a digital pin or send HID)
        elif key == KC.F3:
            obstacle_avoid = not obstacle_avoid
            last_input = "Obstacle On" if obstacle_avoid else "Obstacle Off"
        elif key == KC.F4:
            follow_mode = not follow_mode
            last_input = "Follow On" if follow_mode else "Follow Off"
        elif key == KC.UP:
            last_input = "UP"
        elif key == KC.DOWN:
            last_input = "DOWN"
        elif key == KC.LEFT:
            last_input = "LEFT"
        elif key == KC.RIGHT:
            last_input = "RIGHT"
        elif key == KC.SPACE:
            last_input = "STOP"
        elif key == KC.KP_PLUS:
            # encoder increase speed
            speed = min(100, speed + 5)
            last_input = "ENC +"
        elif key == KC.KP_MINUS:
            # encoder decrease speed
            speed = max(0, speed - 5)
            last_input = "ENC -"
        elif key == KC.ENTER:
            last_input = "ENC BTN"
        else:
            # other keys
            last_input = str(key)

        # refresh OLED after handling
        oled_refresh()

# instantiate robot module
robot_module = RobotModule()

# -----------------------
# Finish keyboard module list and start
# -----------------------
keyboard.modules = [macros, encoder_handler, robot_module]

# some keyboard settings
keyboard.tap_time = 200
keyboard.debug_enabled = False

if __name__ == "__main__":
    keyboard.go()
