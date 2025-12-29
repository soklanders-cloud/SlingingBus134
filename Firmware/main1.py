import board
import busio
import digitalio
import time

import adafruit_ssd1306
import neopixel

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.matrix import DiodeOrientation
from kmk.modules.macros import Macros
from kmk.modules.new_encoder import EncoderHandler

# -----------------------
# Basic keyboard setup
# -----------------------
keyboard = KMKKeyboard()

keyboard.col_pins = (board.GP1, board.GP2, board.GP4)

keyboard.row_pins = (board.GP28, board.GP27, board.GP26)

keyboard.diode_orientation = DiodeOrientation.COL2ROW

keyboard.keymap = [
    [
        KC.F1, KC.UP,   KC.F3,   # row0
        KC.LEFT, KC.SPACE, KC.RIGHT, # row1
        KC.F2, KC.DOWN, KC.F4    # row2
    ]
]

macros = Macros()

encoder = EncoderHandler()
encoder.pins = ((board.GP29, board.GP0, board.GP3, False),)

encoder.map = (
    ((KC.KP_MINUS, KC.KP_PLUS, KC.ENTER),),
)

enc_btn = digitalio.DigitalInOut(board.GP3)
enc_btn.direction = digitalio.Direction.INPUT
enc_btn.pull = digitalio.Pull.UP


OLED_W = 128
OLED_H = 32

oled = None
try:
    i2c = busio.I2C(board.GP7, board.GP6)
    oled = adafruit_ssd1306.SSD1306_I2C(OLED_W, OLED_H, i2c)
    oled.fill(0)
    oled.show()
except Exception as e:
    print("OLED init failed:", e)
    oled = None

try:
    pixels = neopixel.NeoPixel(board.GP5, 4, brightness=0.3, auto_write=True)
    pixels.fill((0, 0, 0))
except Exception:
    pixels = None


led_on = False
obstacle_avoid = False
follow_mode = False
speed = 50
last_input = "None"

def mode_name():
    if follow_mode:
        return "Follow"
    if obstacle_avoid:
        return "Obstacle"
    return "Manual"

def oled_refresh():
    if not oled:
        return
    oled.fill(0)
    oled.text("Mode: {}".format(mode_name()), 0, 0, 1)
    oled.text("Speed: {:3d}%".format(speed), 0, 10, 1)
    oled.text("Last: {}".format(last_input[:18]), 0, 22, 1)
    oled.show()

oled_refresh()


class RobotModule:
    def process_key(self, keyboard_obj, key, is_pressed):
        global led_on, obstacle_avoid, follow_mode, speed, last_input, pixels

        if not is_pressed:
            return

        if key == KC.F1:
            led_on = not led_on
            last_input = "LED ON" if led_on else "LED OFF"
            if pixels is not None:
                pixels.fill((255,255,255) if led_on else (0,0,0))

        elif key == KC.F2:
            last_input = "OPEN DOOR"

        elif key == KC.F3:
            obstacle_avoid = not obstacle_avoid
            last_input = "OBS ON" if obstacle_avoid else "OBS OFF"

        elif key == KC.F4:
            follow_mode = not follow_mode
            last_input = "FOLLOW ON" if follow_mode else "FOLLOW OFF"

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
            last_input = "SPD +"

        elif key == KC.KP_MINUS:
            speed = max(0, speed - 5)
            last_input = "SPD -"

        elif key == KC.ENTER:
            last_input = "ENC BTN"

        else:
            last_input = str(key)

        oled_refresh()

keyboard.modules = [macros, encoder, RobotModule()]
keyboard.tap_time = 200
keyboard.debug_enabled = False

if __name__ == "__main__":
    keyboard.go()
