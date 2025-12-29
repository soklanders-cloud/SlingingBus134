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

keyboard.col_pins = (board.GP1, board.GP2, board.GP4)

keyboard.row_pins = (board.GP28, board.GP27, board.GP26)

keyboard.diode_orientation = DiodeOrientation.COL2ROW

# -----------------------
keyboard.keymap = [
    [
        KC.F1,    KC.UP,   KC.F3,   
        KC.LEFT,  KC.SPACE,KC.RIGHT,
        KC.F2,    KC.DOWN, KC.F4    
    ]
]

macros = Macros()


encoder_handler = EncoderHandler()
encoder_handler.pins = ((board.GP29, board.GP0, board.GP3, False),)
encoder_handler.map = (
    ((KC.KP_MINUS, KC.KP_PLUS, KC.ENTER),), 
)

btn_pin = digitalio.DigitalInOut(board.GP3)
btn_pin.direction = digitalio.Direction.INPUT
btn_pin.pull = digitalio.Pull.UP

OLED_WIDTH = 128
OLED_HEIGHT = 32

oled = None
try:
    i2c = busio.I2C(board.GP7, board.GP6)  
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

led_on = False
obstacle_avoid = False
follow_mode = False
speed = 50 
last_input = "None"

def current_mode_string():
    if follow_mode:
        return "Follow"
    if obstacle_avoid:
        return "Obstacle"
    return "Manual"

def oled_refresh():
    if not oled:
        return
    oled.fill(0)
    oled.text("Mode:{:8}".format(current_mode_string()), 0, 0, 1)
    oled.text("Spd:{:3d}%".format(speed), 80, 0, 1)
    s = "LED:{} O:{:d} F:{:d}".format("On" if led_on else "Off", int(obstacle_avoid), int(follow_mode))
    oled.text(s, 0, 12, 1)
    oled.text("Last:"+last_input[:18], 0, 22, 1)
    oled.show()

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
        pass

    
    def process_key(self, keyboard_obj, key, is_pressed):
        if not is_pressed:
            return

        global led_on, obstacle_avoid, follow_mode, speed, last_input

        if key == KC.F1:
            led_on = not led_on
            last_input = "LED On" if led_on else "LED Off"
        elif key == KC.F2:
            last_input = "Open Door"
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
            speed = min(100, speed + 5)
            last_input = "ENC +"
        elif key == KC.KP_MINUS:
            speed = max(0, speed - 5)
            last_input = "ENC -"
        elif key == KC.ENTER:
            last_input = "ENC BTN"
        else:
            last_input = str(key)

        oled_refresh()


robot_module = RobotModule()

keyboard.modules = [macros, encoder_handler, robot_module]

keyboard.tap_time = 200
keyboard.debug_enabled = False

if __name__ == "__main__":
    keyboard.go()
