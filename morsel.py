from machine import Pin, I2C
from lib.display.ssd1306 import SSD1306_I2C
from lib.neopixel import NeoPixel
from lib.display.scrolling_display import ScrollingDisplay
from lib.buzzer import Buzzer
from lib.morse.morse_straight import StraightKeyer
from lib.morse.morse_iambic import IambicKeyer
from lib.morse.morse_decoder import MorseDecoder
from lib.button import Button
import uasyncio as asyncio

__version__ = (0, 3, 0)

class Morsel:
    
    def __init__(self):
        i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=200000)
        self.oled = SSD1306_I2C(128, 64, i2c)
        self.neo = NeoPixel()
        self.buzzer = Buzzer(27)
        self.row1 = ScrollingDisplay(self.oled,2)
        self.row1.print("Morsel v0.3")
        self.row2 = ScrollingDisplay(self.oled,3,25)
        self.row3 = ScrollingDisplay(self.oled,1,50,70,1,6)
        self.initDecoder()
        self.initIambicKeyer()
        self.initStraightKeyer()
        button1 = Button(4, self.initLeftKey())
        #button1.pb.debounce_ms = 20 # Necessary for straight keying
        button2 = Button(3, self.initRightKey())
        self.buttons = [button1,button2]
    
    def initDecoder(self):
        decoderHandler = {
            ' ': [(self.neo.on,NeoPixel.PURPLE,50)],
            '#': [(self.neo.on,NeoPixel.RED)],
            'Default': [(self.neo.on,NeoPixel.GREEN,10)],
            'Always': [(self.row2.print,{})]
        }
        self.decoder = MorseDecoder(decoderHandler)
    
    def printWpm(self,wpm):
        self.row3.print('wpm:'+'{:0>2}'.format(wpm))
    
    def initStraightKeyer(self):
        sKeyerHandler = {
            StraightKeyer.TONE: [self.buzzer.start,(self.neo.on,NeoPixel.CYAN,10)],
            StraightKeyer.NO_TONE: [self.buzzer.stop,self.neo.off],
            StraightKeyer.DIT: [self.decoder.dit],
            StraightKeyer.DAH: [self.decoder.dah],
            StraightKeyer.END_OF_CHAR: [self.decoder.endOfChar],
            StraightKeyer.END_OF_WORD: [self.decoder.endOfWord],
            StraightKeyer.TOO_SHORT: [],
            StraightKeyer.TOO_LONG: [],
            'Default': [(self.printWpm,{})]
        }
        self.sKeyer = StraightKeyer(sKeyerHandler)
    
    def initStraightKey(self):
        sKeyHandler = {
            Button.DOWN: [self.sKeyer.straightKeyDown],
            Button.UP: [self.sKeyer.straightKeyUp]
        }
        return sKeyHandler
    
    def initLeftKey(self):
        iLeftKeyHandler = {
            Button.DOWN: [self.iKeyer.startPlayingDits],
            Button.UP: [self.iKeyer.stopPlayingDits]
        }
        return iLeftKeyHandler
    
    def initRightKey(self):
        iRightKeyHandler = {
            Button.DOWN: [self.iKeyer.startPlayingDahs],
            Button.UP: [self.iKeyer.stopPlayingDahs]
        }
        return iRightKeyHandler   
    
    def initIambicKeyer(self):
        self.iKeyerHandler = {
            IambicKeyer.TONE: [self.buzzer.start],
            IambicKeyer.NO_TONE: [self.buzzer.stop,self.neo.off],
            IambicKeyer.DIT: [self.decoder.dit,(self.neo.on,NeoPixel.BLUE,10)],
            IambicKeyer.DAH: [self.decoder.dah,(self.neo.on,NeoPixel.YELLOW,10)],
            IambicKeyer.END_OF_CHAR: [self.decoder.endOfChar],
            IambicKeyer.END_OF_WORD: [self.decoder.endOfWord],
            'Default': [(self.printWpm,{})]
        }
        self.iKeyerHandlerToneOnly = {
            IambicKeyer.TONE: [self.buzzer.start],
            IambicKeyer.NO_TONE: [self.buzzer.stop,self.neo.off],
            IambicKeyer.DIT: [(self.neo.on,NeoPixel.BLUE,10)],
            IambicKeyer.DAH: [(self.neo.on,NeoPixel.YELLOW,10)],
            IambicKeyer.END_OF_CHAR: [],
            IambicKeyer.END_OF_WORD: [],
            'Default': [(self.printWpm,{})]
        }
        self.iKeyer = IambicKeyer(self.iKeyerHandlerToneOnly)
    
    async def run(self):
        self.iKeyer.setWpm(25)

        await self.iKeyer.play('QRV')
        await asyncio.sleep_ms(500) # to avoid last space printed on screen
        self.iKeyer.switchHandler(self.iKeyerHandler)
        #iKeyer.setMode(IambicKeyer.MODE_B)
        while True:
            await asyncio.sleep_ms(100)
