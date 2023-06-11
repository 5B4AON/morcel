from ws2812 import WS2812
from machine import Pin

class NeoPixel: # NeoPixel on XIAO rp2040

    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 150, 0)
    GREEN = (0, 255, 0)
    CYAN = (0, 255, 255)
    BLUE = (0, 0, 255)
    PURPLE = (180, 0, 255)
    WHITE = (255, 255, 255)

    def __init__(self):
        self.ledPower = Pin(11, Pin.OUT)
        self.led = WS2812(12,1)#WS2812(pin_num,led_count)

    def applyColorLevel(self,color,divider):
        r = int(round(color[0] / divider))
        y = int(round(color[1] / divider))
        b = int(round(color[2] / divider))
        return (r, y, b)

    def on(self,color=WHITE,divider=1):
        self.ledPower.value(1)
        self.led.pixels_fill(self.applyColorLevel(color,divider))
        self.led.pixels_show()

    def off(self):
            self.ledPower.value(0)
