import board
import displayio
import terminalio
import busio
from digitalio import DigitalInOut, Direction, Pull

from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners.keypad import MatrixScanner
from kmk.keys import KC
from kmk.modules.encoder import EncoderHandler

from adafruit_display_text import label
from adafruit_ssd1306 import SSD1306_I2C

keyboard = KMKKeyboard()

row_pins = (board.GP28, board.GP27, board.GP26)   # R0, R1, R2

col_pins = (board.GP1, board.GP2, board.GP4)      # C0, C1, C2

keyboard.matrix = MatrixScanner(
    row_pins=row_pins,
    col_pins=col_pins,
    value_when_pressed=False,
)

F_UP        = KC.F13
F_DOWN      = KC.F14
F_LEFT      = KC.F15
F_RIGHT     = KC.F16
F_STOP      = KC.F17
F_LED       = KC.F18
F_DOOR      = KC.F19
F_OBS_TOG   = KC.F20
F_CAM_TOG   = KC.F21   

# row0: up-left, up, up-right
# row1: left,   stop, right
# row2: dn-left, dn, dn-right
keyboard.keymap = [[
    [F_LED,   F_UP,    F_OBS_TOG],   # Row 0
    [F_LEFT,  F_STOP,  F_RIGHT],     # Row 1
    [F_DOOR,  F_DOWN,  F_CAM_TOG],   # Row 2
]]

state = {
    "mode": "STOP",      # movement state
    "speed": 0,          # encoder-controlled speed value
    "camera": False,     # camera on/off
    "obstacle": False,   # obstacle-avoid on/off
    "last_input": "None"
}

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

# OLED: 0.91" SSD1306

i2c = busio.I2C(board.GP7, board.GP6)  # SCL, SDA
displayio.release_displays()
display = SSD1306_I2C(128, 32, i2c)

splash = displayio.Group()
display.show(splash)

text_area = label.Label(
    terminalio.FONT,
    text="Init...",
    color=0xFFFFFF,
    x=0,
    y=8,
)
splash.append(text_area)

def update_oled():
    text_area.text = (
        "Mode: " + state["mode"] +
        "
Spd: " + str(state["speed"]) +
        "
Last: " + state["last_input"]
    )

update_oled()

# rotary encoder

encoder = EncoderHandler()
encoder.pins = (
    (board.GP29, board.GP0, None),  # A, B, (button handled separately)
)

encoder.map = [
    ((KC.NO,), (KC.NO,)),
]
keyboard.modules.append(encoder)
enc_btn = DigitalInOut(board.GP3)
enc_btn.direction = Direction.INPUT
enc_btn.pull = Pull.UP
enc_btn_last = True

def handle_encoder_speed():
    global last_encoder_position
    diff = encoder.get_position(0)
    if diff != 0:
        # positive diff = CW, negative = CCW
        state["speed"] = clamp(state["speed"] + diff, 0, 10)
        state["last_input"] = "Speed " + ("+" if diff > 0 else "-")
        update_oled()

def handle_encoder_button():
    global enc_btn_last
    current = enc_btn.value
    if enc_btn_last and not current:
        state["mode"] = "STOP"
        state["last_input"] = "ENC BTN"
        update_oled()
    enc_btn_last = current

def set_mode(new_mode, label):
    state["mode"] = new_mode
    state["last_input"] = label
    update_oled()

def toggle_obstacle(label):
    state["obstacle"] = not state["obstacle"]
    state["last_input"] = f"{label}: " + ("ON" if state["obstacle"] else "OFF")
    update_oled()
    
def toggle_camera(label):
    state["camera"] = not state["camera"]
    state["last_input"] = f"{label}: " + ("ON" if state["camera"] else "OFF")
    update_oled()

def process_function_key(keycode):
    if   keycode is F_UP:       set_mode("FORWARD", "UP")
    elif keycode is F_DOWN:     set_mode("BACK", "DOWN")
    elif keycode is F_LEFT:     set_mode("LEFT", "LEFT")
    elif keycode is F_RIGHT:    set_mode("RIGHT", "RIGHT")
    elif keycode is F_STOP:     set_mode("STOP", "STOP")
    elif keycode is F_LED:      set_mode(state["mode"], "LED TOGGLE")
    elif keycode is F_DOOR:     set_mode(state["mode"], "OPEN DOOR")
    elif keycode is F_OBS_TOG:  toggle_obstacle("OBSTACLE")
    elif keycode is F_CAM_TOG:  toggle_camera("CAMERA")

def scan_keys():
    for event in keyboard.matrix.events.get():
        if event.pressed:
            kc = keyboard.keymap[0][event.row][event.col]
            process_function_key(kc)

keyboard.debounce_time = 20

if __name__ == "__main__":
    while True:
        keyboard.tick()
        scan_keys()
        handle_encoder_speed()
        handle_encoder_button()
