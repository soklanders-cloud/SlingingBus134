import board
import busio
import digitalio

import adafruit_ssd1306
import neopixel

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.matrix import DiodeOrientation
from kmk.modules.macros import Macros
from kmk.modules.new_encoder import EncoderHandler

keyboard = KMKKeyboard()

keyboard.col_pins = (board.GP1, board.GP2, board.GP4)
keyboard.row_pins = (board.GP28, board.GP27, board.GP26)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

keyboard.keymap = [
    [
        KC.F1, KC.UP,   KC.F3,
        KC.LEFT, KC.SPACE, KC.RIGHT,
        KC.F2, KC.DOWN, KC.F4
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

oled = None
try:
    i2c = busio.I2C(board.GP7, board.GP6)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
    oled.fill(0)
    oled.show()
except Exception as e:
    print("OLED not detected:", e)

try:
    pixels = neopixel.NeoPixel(board.GP5, 4, brightness=0.3, auto_write=True)
    pixels.fill((0, 0, 0))
except Exception:
    pixels = None

led_on = False
obstacle_avoid = False
camera_on = False
speed = 50
last_input = "None"

def current_mode():
    return "Obstacle" if obstacle_avoid else "Manual"

def oled_update():
    if not oled:
        return

    oled.fill(0)
    oled.text(f"Mode: {current_mode()}", 0, 0, 1)
    oled.text(f"Speed: {speed:3d}%", 0, 10, 1)
    oled.text(f"Cam: {'ON' if camera_on else 'OFF'}", 80, 10, 1)
    oled.text(f"Last: {last_input[:18]}", 0, 22, 1)
    oled.show()

oled_update()

class RobotModule:
    def process_key(self, keyboard, key, pressed):
        global led_on, obstacle_avoid, camera_on, speed, last_input

        if not pressed:
            return

        if key == KC.F1:
            led_on = not led_on
            last_input = "LED ON" if led_on else "LED OFF"
            if pixels:
                pixels.fill((255, 255, 255) if led_on else (0, 0, 0))

        elif key == KC.F2:
            last_input = "OPEN DOOR"

        elif key == KC.F3:
            obstacle_avoid = not obstacle_avoid
            last_input = "OBS ON" if obstacle_avoid else "OBS OFF"

        elif key == KC.F4:
            camera_on = not camera_on
            last_input = "CAM ON" if camera_on else "CAM OFF"

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

        oled_update()

keyboard.modules = [macros, encoder, RobotModule()]
keyboard.tap_time = 200
keyboard.debug_enabled = False

if __name__ == "__main__":
    keyboard.go()
