from machine import Pin
from lib.abutton import Pushbutton
from lib.callback_handler import CallBackHandler

__version__ = (0, 1, 0)
class Button:
    UP = 1
    DOWN = 2
    LONG = 3
    DOUBLE = 4
    
    defaultHandler = {
        DOWN: [(print,'DOWN')],
        UP: [(print,'UP')],
        LONG: [(print,'LONG')],
        DOUBLE: [(print,'DOUBLE')]
    }
    
    def __init__(self,pin,handler=defaultHandler):
        self.callbackHandler = CallBackHandler(handler)
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.pb = Pushbutton(self.pin)
        self.pb.debounce_ms = 2
        self.pb.double_click_ms = 400
        self.pb.long_press_ms = 800
        self.pb.press_func(self.callbackHandler, (Button.DOWN,))
        self.pb.release_func(self.callbackHandler, (Button.UP,))
        #self.pb.long_func(self.callbackHandler, (Button.LONG,))
        #self.pb.double_func(self.callbackHandler, (Button.DOUBLE,))

    def switchHandler(self,handler):
        self.callbackHandler = CallBackHandler(handler)

