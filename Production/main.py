import board
import busio
import time
import displayio
import terminalio
import adafruit_displayio_ssd1306
import framebuf
from adafruit_display_text import label
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.handlers.sequences import send_string, simple_key_sequence
from kmk.modules.encoder import EncoderHandler
from kmk.modules.layers import Layers
from kmk.matrix import DiodeOrientation

keyboard = KMKKeyboard()

# --------------------
# MATRIX
# Cols: GP26 (A0), GP27 (A1), GP28 (A2)
# Rows: GP1, GP2, GP3, GP4
# Encoder A: GP29 (SWa), Encoder B: GP0 (SWb) — per schematic
# OLED I2C: GP6 (SDA), GP7 (SCL) — per J1 connector
# --------------------
keyboard.col_pins = (board.GP26, board.GP27, board.GP28)
keyboard.row_pins = (board.GP1, board.GP2, board.GP3, board.GP4)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

# --------------------
# MODULES
# --------------------
layers = Layers()
keyboard.modules.append(layers)

encoder = EncoderHandler()
keyboard.modules.append(encoder)

# Encoder A=GP29, B=GP0, push button handled by matrix (SW12)
encoder.pins = ((board.GP29, board.GP0, None),)
encoder.map = [
    ((KC.VOLD, KC.VOLU),)
]

# --------------------
# OLED SETUP
# Uses GP6 (SDA) and GP7 (SCL) — dedicated I2C pins, no conflict
# --------------------
displayio.release_displays()
i2c = busio.I2C(scl=board.GP7, sda=board.GP6)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

# Framebuffer for pixel-level animation control
fbuf_data = bytearray(128 * 32 // 8)
fb = framebuf.FrameBuffer(fbuf_data, 128, 32, framebuf.MONO_HLSB)

# --------------------
# ANIMATION FRAMES
# --------------------
FRAME1 = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 192, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 56, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 128, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 32, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 6, 64, 0, 1, 142, 0, 0, 0, 0, 120, 0, 0, 0, 0, 0, 0, 1, 128, 0, 0, 33, 0, 0, 0, 7, 128, 0, 0, 0, 0, 0, 0, 64, 0, 0, 0, 36, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 64, 0, 0, 0, 81, 128, 0, 23, 0, 0, 0, 0, 0, 0, 0, 0, 64, 0, 0, 24, 76, 128, 0, 224, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, 140, 128, 30, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 0, 0, 0, 0, 129, 224, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 115, 0, 64, 129, 94, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, 168, 17, 192, 0, 224, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 17, 8, 12, 0, 78, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 148, 0, 3, 240, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 34, 100, 0, 124, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 66, 96, 6, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64, 4, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64, 11, 192, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 88, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 143, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 224, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 248, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 112, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
FRAME2 = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 192, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 56, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 32, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 6, 64, 0, 1, 0, 0, 0, 0, 0, 56, 0, 0, 0, 0, 0, 0, 64, 128, 0, 0, 64, 0, 0, 0, 3, 128, 0, 0, 0, 0, 0, 0, 64, 0, 0, 0, 32, 0, 0, 0, 184, 0, 0, 0, 0, 0, 0, 0, 64, 0, 0, 0, 16, 0, 0, 31, 0, 0, 0, 0, 0, 0, 0, 0, 64, 0, 0, 16, 8, 0, 1, 224, 0, 0, 0, 0, 0, 0, 0, 0, 32, 0, 0, 24, 4, 0, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 224, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 115, 0, 128, 1, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, 138, 19, 64, 0, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 17, 8, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 33, 164, 0, 3, 0, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 100, 0, 92, 64, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 100, 7, 128, 51, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64, 4, 56, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64, 15, 192, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 151, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 224, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 192, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 56, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 240, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 31, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
FRAME3 = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 192, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 120, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 128, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 32, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 38, 64, 0, 1, 150, 0, 0, 0, 0, 120, 0, 0, 0, 0, 0, 0, 65, 128, 0, 0, 97, 0, 0, 0, 7, 128, 0, 0, 0, 0, 0, 0, 64, 0, 0, 0, 36, 128, 0, 0, 248, 0, 0, 0, 0, 0, 0, 0, 64, 0, 0, 0, 81, 128, 0, 14, 0, 0, 0, 0, 0, 0, 0, 0, 64, 0, 0, 24, 76, 128, 1, 224, 0, 0, 0, 0, 0, 0, 0, 0, 32, 0, 0, 16, 140, 128, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 0, 0, 0, 128, 129, 160, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 3, 0, 0, 128, 30, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, 3, 19, 192, 1, 224, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, 0, 8, 0, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 0, 0, 2, 224, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 0, 0, 124, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64, 0, 7, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64, 0, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64, 0, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128, 0, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 159, 128, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 160, 96, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 46, 0, 24, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 192, 0, 5, 192, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 120, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 240, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 31, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
FRAME4 = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 192, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 120, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 6, 64, 0, 1, 128, 0, 0, 0, 0, 56, 0, 0, 0, 0, 0, 0, 65, 128, 0, 0, 64, 0, 0, 0, 7, 128, 0, 0, 0, 0, 0, 0, 64, 0, 0, 0, 32, 0, 0, 0, 248, 0, 0, 0, 0, 0, 0, 0, 64, 0, 0, 0, 16, 0, 0, 29, 0, 0, 0, 0, 0, 0, 0, 0, 64, 0, 0, 24, 8, 0, 1, 224, 0, 0, 0, 0, 0, 0, 0, 0, 32, 0, 0, 24, 4, 0, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 0, 0, 0, 2, 1, 96, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 2, 0, 0, 1, 30, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, 3, 19, 192, 1, 224, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 0, 0, 1, 0, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32, 0, 0, 188, 128, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64, 0, 7, 128, 57, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64, 0, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64, 0, 64, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128, 0, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 141, 128, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 224, 96, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 62, 0, 24, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 192, 0, 7, 192, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 240, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 31, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

frames = [FRAME1, FRAME2, FRAME3, FRAME4]
frame_index = 0
last_frame_time = time.monotonic()
FRAME_DELAY = 0.15

# --------------------
# Helper: push frame data to OLED via displayio bitmap
# --------------------
def show_frame(frame_bytes):
    # Create a displayio group with a bitmap built from the raw frame bytes
    group = displayio.Group()
    bitmap = displayio.Bitmap(128, 32, 2)
    palette = displayio.Palette(2)
    palette[0] = 0x000000  # black
    palette[1] = 0xFFFFFF  # white

    for byte_index, byte in enumerate(frame_bytes):
        for bit in range(8):
            pixel_index = byte_index * 8 + bit
            if pixel_index >= 128 * 32:
                break
            x = pixel_index % 128
            y = pixel_index // 128
            bitmap[x, y] = (byte >> (7 - bit)) & 1

    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
    group.append(tile_grid)
    display.root_group = group

# --------------------
# MACROS
# --------------------
def open_app(path):
    """Launch a Windows app or URL using Win + R."""
    return simple_key_sequence([
        KC.LGUI(KC.R),
        0.2,
        send_string(path + '\n'),
    ])

SCREENSHOT = KC.LGUI(KC.LSFT(KC.S))
ALT_F7     = KC.LALT(KC.F7)

MODRINTH = open_app(r"C:\Users\feint\AppData\Local\Modrinth App\Modrinth App.exe")
DISCORD  = open_app(r"C:\Users\feint\AppData\Local\Discord\Update.exe --processStart Discord.exe")
LUNAR    = open_app(r"C:\Users\feint\AppData\Local\Programs\Lunar Client\Lunar Client.exe")
YOUTUBE  = open_app("https://www.youtube.com")
OBS      = open_app(r"C:\Program Files\obs-studio\bin\64bit\obs64.exe")
GCHAT    = open_app("https://chat.google.com")

# --------------------
# KEYMAP
# 4 rows x 3 cols = 12 keys
# Row 0: SW1,  SW2,  SW3
# Row 1: SW4,  SW5,  SW6
# Row 2: SW7,  SW8,  SW9
# Row 3: SW10, SW11, SW12 (encoder push)
# --------------------
keyboard.keymap = [
    [
        LUNAR,      MODRINTH,   DISCORD,    # Row 0
        OBS,        SCREENSHOT, ALT_F7,     # Row 1
        KC.UNDO,    KC.COPY,    KC.PASTE,   # Row 2
        YOUTUBE,    GCHAT,      KC.MUTE,    # Row 3 — SW12 = encoder push
    ]
]

# --------------------
# ANIMATION EXTENSION
# --------------------
class AnimationExtension:
    def during_bootup(self, keyboard):
        show_frame(frames[0])

    def before_matrix_scan(self, keyboard):
        global frame_index, last_frame_time
        now = time.monotonic()
        if now - last_frame_time >= FRAME_DELAY:
            show_frame(frames[frame_index])
            frame_index = (frame_index + 1) % len(frames)
            last_frame_time = now

    def after_matrix_scan(self, keyboard):
        pass

    def before_hid_send(self, keyboard):
        pass

    def after_hid_send(self, keyboard):
        pass

    def on_powersave_enable(self, keyboard):
        display.root_group = displayio.Group()  # blank screen

    def on_powersave_disable(self, keyboard):
        show_frame(frames[frame_index])

keyboard.extensions.append(AnimationExtension())

# --------------------
# START
# --------------------
if __name__ == "__main__":
    keyboard.go()
