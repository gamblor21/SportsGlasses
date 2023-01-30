import is31fl3741
import displayio
import framebufferio
import board
import busio
import time
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from rainbowio import colorwheel
from map import glassesmatrix_ledmap, left_ring_map, right_ring_map, left_ring_map_no_display, right_ring_map_no_display
from IS31FL3741_Strip import IS31FL3741
from random import randint
import random
from adafruit_led_animation.animation.comet import Comet
from adafruit_debouncer import Debouncer
import digitalio

def TouchDown(color, ring_color, repeat, delay):
    comet_left = Comet(strip_left, speed=0.01, color=ring_color, tail_length=20, bounce=True)
    comet_right = Comet(strip_right, speed=0.01, color=ring_color, tail_length=20, bounce=True)

    text_area = label.Label(font, text="TOUCHDOWN!!!", color=color)
    x = display.width
    text_area.x = x
    text_area.y = 8
    group.append(text_area)
    display.show(group)

    width = text_area.bounding_box[2]
    for i in range(repeat):
        print(i)
        while x != - width:
            x = x - 1
            text_area.x = x
            if x % 6:
                comet_left.animate()
                comet_right.animate()
            time.sleep(delay)
        while x != display.width:
            x = x + 1
            text_area.x = x
            if x % 6:
                comet_left.animate()
                comet_right.animate()
            time.sleep(delay)

    group.remove(text_area)

def FillRings(lcolor, rcolor):
    strip_left.fill(lcolor)
    strip_right.fill(rcolor)
    strip_left.show()
    strip_right.show()

def Jitter(upper):
    return random.random() * upper

def Blink(color, ring_color, blinks, jit, delay):
    strip_left.fill(ring_color)
    strip_right.fill(ring_color)

    bitmap = displayio.Bitmap(display.width, display.height, 3)
    palette = displayio.Palette(3)
    palette[0] = 0x000000
    palette[1] = color
    palette[2] = ring_color
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
    for x in range(display.width):
        for y in range(display.height):
            bitmap[x,y] = 1
    group.append(tile_grid)
    display.show(group)

    strip_left.show()
    strip_right.show()

    switch.update()
    if switch.value == False:
        group.remove(tile_grid)
        return
    time.sleep(delay)

    for i in range(blinks):
        for y in range(display.height):
            for x in range(display.width):
                bitmap[x,y] = 2
            time.sleep(0.005)
        switch.update()
        if switch.value == False:
            group.remove(tile_grid)
            return
        for y in range(display.height-1, -1, -1):
            for x in range(display.width):
                bitmap[x,y] = 1
            time.sleep(0.005)
        time.sleep(delay+Jitter(jit))
        switch.update()
        if switch.value == False:
            group.remove(tile_grid)
            return

    switch.update()
    if switch.value == False:
        group.remove(tile_grid)
        return
    time.sleep(delay)

    group.remove(tile_grid)

def HalfAndHalf(color1, color2, delay):
    bitmap = displayio.Bitmap(display.width, display.height, 3)
    palette = displayio.Palette(3)
    palette[0] = 0x000000
    palette[1] = color1
    palette[2] = color2
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
    half_width = int(display.width/2)
    for y in range(display.height):
        for x in range(half_width):
            bitmap[x,y] = 1
            bitmap[x+half_width,y] = 2
    group.append(tile_grid)
    display.show(group)

    FillRings(color1, color2)

    switch.update()
    if switch.value == False:
        group.remove(tile_grid)
        return
    time.sleep(delay)
    group.remove(tile_grid)


def Solid(color, ring_color, delay):
    bitmap = displayio.Bitmap(display.width, display.height, 2)
    palette = displayio.Palette(2)
    palette[0] = 0x000000
    palette[1] = color
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
    for x in range(display.width):
        for y in range(display.height):
            bitmap[x,y] = 1
    group.append(tile_grid)
    display.show(group)

    FillRings(ring_color, ring_color)

    switch.update()
    if switch.value == False:
        group.remove(tile_grid)
        return
    time.sleep(delay)
    group.remove(tile_grid)


def ScrollMessage(text, color, repeat, delay):
    text_area = label.Label(font, text=text, color=color)
    x = display.width
    text_area.x = x
    text_area.y = 8
    group.append(text_area)
    display.show(group)

    width = text_area.bounding_box[2]
    for i in range(repeat):
        while x != - width:
            x = x - 1
            text_area.x = x
            switch.update()
            if switch.value == False:
                group.remove(text_area)
                return
            time.sleep(delay)
        x = display.width

    group.remove(text_area)

displayio.release_displays()

pin = digitalio.DigitalInOut(board.SWITCH)
pin.direction = digitalio.Direction.INPUT
pin.pull = digitalio.Pull.UP
switch = Debouncer(pin)

i2c = busio.I2C(board.SCL, board.SDA, frequency=1000000)
is31 = is31fl3741.IS31FL3741(width=54, height=15, i2c=i2c, scale=True, gamma=True, mapping=glassesmatrix_ledmap)
display = framebufferio.FramebufferDisplay(is31, auto_refresh=True)
strip_left = IS31FL3741(i2c, left_ring_map_no_display, 24, init=False, auto_write=False)
strip_right = IS31FL3741(i2c, right_ring_map_no_display, 24, init=False, auto_write=False)

is31.brightness = 1.0

font = bitmap_font.load_font("tfont.bdf")

group = displayio.Group()
display.show(group)

messages = (
    "GO BOMBERS GO",
    "FOR THE W",
    "DEFEND THE CUP",
    "WINNIPEG BLUE BOMBERS",
    "11 TIME CHAMPIONS",
)
BLUE_TEXT = (0,20,255)
BLUE_RING = (0,10,120)
YELLOW_TEXT = (220, 220, 0)
YELLOW_RING = (150,150,0)

while True:
    print("Update")
    switch.update()
    print(switch.value)
    if switch.value == False: # pressed
        FillRings(BLUE_TEXT, BLUE_TEXT)
        TouchDown(YELLOW_TEXT, BLUE_RING, 1, 0.00)
        switch.update()
        FillRings(BLUE_RING, BLUE_RING)
        ScrollMessage("TOUCHDOWN!!!", YELLOW_TEXT, 2, 0.015)
        continue

    action = random.randrange(0,19)

    if action < 5:
        FillRings(BLUE_RING, BLUE_RING)
        ScrollMessage(random.choice(messages), YELLOW_TEXT, 2, 0.015)
    elif action < 10:
        FillRings(YELLOW_RING, YELLOW_RING)
        ScrollMessage(random.choice(messages), BLUE_TEXT, 2, 0.015)
    elif action < 13:
        Blink(YELLOW_RING, BLUE_TEXT, 3, 1.5, 1.5)
    elif action < 16:
        Blink(BLUE_TEXT, YELLOW_RING, 3, 1.5, 1.5)
    elif action == 17:
        HalfAndHalf(BLUE_TEXT, YELLOW_TEXT, 10)
    elif action == 18:
        HalfAndHalf(YELLOW_TEXT, BLUE_TEXT, 10)
    elif action == 19:
        Solid(YELLOW_RING, BLUE_TEXT, 2)
    elif action == 20:
        Solid(BLUE_TEXT, YELLOW_RING, 2)