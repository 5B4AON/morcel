import time
from lib.callback_handler import CallBackHandler
from machine import Timer

#   Dit: 1 unit
#   Dah: 3 units
#   Intra-character space (the gap between dits and dahs within a character): 1 unit
#   Inter-character space (the gap between the characters of a word): 3 units
#   Word space (the gap between two words): 7 units
#   Characters consist of elements (dits,dahs) that always have a trailing Intra-character space

__version__ = (0, 2, 0)
class StraightKeyer:
    
    # Events
    NO_TONE = 0
    TONE = 1
    DIT = 2
    DAH = 3
    END_OF_CHAR = 4
    END_OF_WORD = 5
    TOO_SHORT = 6
    TOO_LONG = 7

    defaultHandler = {
        NO_TONE: [(print,'NO_TONE')],
        TONE: [(print,'TONE')],
        DIT: [(print,'DIT')],
        DAH: [(print,'DAH')],
        END_OF_CHAR: [(print,'END_OF_CHAR')],
        END_OF_WORD: [(print,'END_OF_WORD')],
        TOO_SHORT: [(print,'TOO_SHORT')],
        TOO_LONG: [(print,'TOO_LONG')]
    }

    def __init__(self,handler=defaultHandler):
        self.callback = CallBackHandler(handler)
        self.setWpm(17) # WPM count (will self adjust)
        self.startDownTime = 0
        self.downTime = 0
        self.endOfCharTimeout = Timer()
        self.endOfWordTimeout = Timer()
        self.maxDAH = 400 # (millis) This is the DAH length at 9 words per minute
        self.minDIT = 33 # (millis) This is the DIT length at 36 words per minute

    def switchHandler(self,handler):
        self.callback = CallBackHandler(handler)

    def setWpm(self,wpm):
        if wpm < 10:
            print('Try to stay above 10wpm')
            wpm = 10
        if wpm > 35:
            print('Try to stay below 35wpm')
            wpm = 35
        self.unitLength = int(60000 / (wpm * 50)) # (millis) Using PARIS as a word (i.e. 50 units per word)
        self.averageDAH = self.unitLength * 3
        self.averageDIT = self.unitLength
        self.callback(self.getWpm())

    def getWpm(self):
        return int(60000 / (self.unitLength * 50))

    def straightKeyDown(self):
        #print('Key Down')
        self.callback(StraightKeyer.TONE)
        self.startDownTime = time.ticks_ms()
        self.endOfCharTimeout.deinit()
        self.endOfWordTimeout.deinit()

    def straightKeyUp(self):
        #print('Key Up')
        self.callback(StraightKeyer.NO_TONE)
        self.downTime = time.ticks_ms() - self.startDownTime
        self.startDownTime = 0
        self.evaluateDownTime()
        self.endOfCharTimeout.init(mode=Timer.ONE_SHOT,period=int(self.unitLength * 1.7),callback=self.endOfChar)
        self.endOfWordTimeout.init(mode=Timer.ONE_SHOT,period=int(self.unitLength * 4.7),callback=self.endOfWord)
    
    def endOfChar(self,timer):
        #print('End Of Character')
        self.callback(StraightKeyer.END_OF_CHAR)
    
    def endOfWord(self,timer):
        #print('End Of Word')
        self.callback(StraightKeyer.END_OF_WORD)

    def evaluateDownTime(self):
        if self.downTime > self.unitLength * 2:
            self.callback(StraightKeyer.DAH)
            self.adjustBasedOnDAH()
        else:
            self.callback(StraightKeyer.DIT)
            self.adjustBasedOnDIT()
        self.callback(self.getWpm())

    def adjustBasedOnDAH(self):
        if self.downTime < self.maxDAH:
            self.averageDAH = int((self.downTime + self.averageDAH * 2) / 3)
            self.averageDIT = int(self.averageDAH / 3)
            self.unitLength = self.averageDIT
        else:
            self.callback(StraightKeyer.TOO_LONG)

    def adjustBasedOnDIT(self):
        if self.downTime > self.minDIT:
            self.averageDIT = int((self.downTime + self.averageDIT * 2) / 3)
            self.averageDAH = self.averageDIT * 3
            self.unitLength = self.averageDIT
        else:
            self.callback(StraightKeyer.TOO_SHORT)



