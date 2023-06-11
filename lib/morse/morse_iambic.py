from lib.callback_handler import CallBackHandler
from lib.morse.morse_alphabet import DIT,DAH,END_OF_WORD,charToSymbol
from lib.scroll_buffer import ScrollBuffer
from machine import Timer
import uasyncio as asyncio

#   Dit: 1 unit
#   Dah: 3 units
#   Intra-character space (the gap between dits and dahs within a character): 1 unit
#   Inter-character space (the gap between the characters of a word): 3 units
#   Word space (the gap between two words): 7 units
#   Characters consist of elements (dits,dahs) that always have a trailing Intra-character space

__version__ = (0, 3, 0)
class IambicKeyer:
    # Modes
    MODE_A = 0 # When releasing both keys no additional element is sent
    MODE_B = 1 # When releasing both keys an additional element is sent
    # States
    STATE_QUIET = 0
    STATE_DITS = 1
    STATE_DAHS = 2
    STATE_IAMBIC = 3
    # Events
    NO_TONE = 0
    TONE = 1
    DIT = 2
    DAH = 3
    END_OF_CHAR = 4
    END_OF_WORD = 5
    
    defaultHandler = {
        NO_TONE: [(print,'NO_TONE')],
        TONE: [(print,'TONE')],
        DIT: [(print,'DIT')],
        DAH: [(print,'DAH')],
        END_OF_CHAR: [(print,'END_OF_CHAR')],
        END_OF_WORD: [(print,'END_OF_WORD')]
    }

    def __init__(self,handler=defaultHandler):
        self.callback = CallBackHandler(handler)
        self.mode = IambicKeyer.MODE_A
        self.setWpm(17) # WPM count
        self.buffer = ScrollBuffer(20) # Queue up to 20 future state changes
        self.running = False
        self.currentState = IambicKeyer.STATE_QUIET
        self.previousState = self.currentState
        self.currentElement = None
        self.toneTimeout = Timer()
        self.elementTimeout = Timer()
        self.endOfCharTimeout = Timer()
        self.endOfWordTimeout = Timer()
        self.initStateHandler()

    def switchHandler(self,handler):
        self.callback = CallBackHandler(handler)

    def setWpm(self,wpm):
        if wpm < 10:
            print('Try to stay above 10wpm')
            wpm = 10
        if wpm > 50:
            print('Try to stay below 50wpm')
            wpm = 50
        self.unitLength = int(60000 / (wpm * 50)) # (millis) Using PARIS as a word (i.e. 50 units per word)
        self.callback(self.getWpm())

    def getWpm(self):
        return int(60000 / (self.unitLength * 50))

    def setMode(self,mode):
        self.mode = mode

    def wakeUp(self):
        #print('Waking up...')
        if not self.running and self.currentState == IambicKeyer.STATE_QUIET:
            self.next()

    def enqueue(self,state):
        self.previousState = state
        self.buffer.enqueue(self.previousState)

    def startPlayingDits(self):
        state = self.previousState
        if state == IambicKeyer.STATE_QUIET:
            self.enqueue(IambicKeyer.STATE_DITS)
            self.wakeUp()
        elif state == IambicKeyer.STATE_DAHS:
            self.enqueue(IambicKeyer.STATE_IAMBIC)

    def startPlayingDahs(self):
        state = self.previousState
        if state == IambicKeyer.STATE_QUIET:
            self.enqueue(IambicKeyer.STATE_DAHS)
            self.wakeUp()
        elif state == IambicKeyer.STATE_DITS:
            self.enqueue(IambicKeyer.STATE_IAMBIC)
        
    def stopPlayingDits(self):
        state = self.previousState
        if state == IambicKeyer.STATE_DITS:
            self.enqueue(IambicKeyer.STATE_QUIET)
        elif state == IambicKeyer.STATE_IAMBIC:
            self.enqueue(IambicKeyer.STATE_DAHS)
        
    def stopPlayingDahs(self):
        state = self.previousState
        if state == IambicKeyer.STATE_DAHS:
            self.enqueue(IambicKeyer.STATE_QUIET)
        elif state == IambicKeyer.STATE_IAMBIC:
            self.enqueue(IambicKeyer.STATE_DITS)
            
    def endOfChar(self,timer):
        #print('End Of Character')
        self.callback(IambicKeyer.END_OF_CHAR)
    
    def endOfWord(self,timer):
        #print('End Of Word')
        self.callback(IambicKeyer.END_OF_WORD)

    def stopTone(self,timer):
        #print('Stopping Tone')
        self.callback(IambicKeyer.NO_TONE)
        self.endOfCharTimeout.init(mode=Timer.ONE_SHOT,period=int(self.unitLength * 1.1),callback=self.endOfChar)
        self.endOfWordTimeout.init(mode=Timer.ONE_SHOT,period=int(self.unitLength * 6),callback=self.endOfWord)

    def playDIT(self):
        self.enqueue(IambicKeyer.STATE_DITS)
        self.enqueue(IambicKeyer.STATE_QUIET)
        self.wakeUp()
    
    def playDAH(self):
        self.enqueue(IambicKeyer.STATE_DAHS)
        self.enqueue(IambicKeyer.STATE_QUIET)
        self.wakeUp()

    def initStateHandler(self):
        stateHandlerBehaviour = {
            IambicKeyer.STATE_DITS: [self.startDIT],
            IambicKeyer.STATE_DAHS: [self.startDAH],
            IambicKeyer.STATE_IAMBIC: [self.startIAMBIC],
            IambicKeyer.STATE_QUIET: [self.startQUIET]
        }
        self.stateHandler = CallBackHandler(stateHandlerBehaviour)

    def endElement(self,timer=None):
        #print('Ending Element')
        # Add another element if dropping out of IAMBIC and we are at MODE B
        if self.mode == IambicKeyer.MODE_B and self.previousState == IambicKeyer.STATE_IAMBIC and not self.currentState == IambicKeyer.STATE_IAMBIC:
            if self.currentElement == IambicKeyer.DAH:
                self.enqueue(IambicKeyer.STATE_DITS)
                self.enqueue(IambicKeyer.STATE_IAMBIC)
            elif self.currentElement == IambicKeyer.DIT:
                self.enqueue(IambicKeyer.STATE_DAHS)
                self.enqueue(IambicKeyer.STATE_IAMBIC)
        if self.buffer.isEmpty():
            self.stateHandler(self.currentState) # keep doing same thing
        else:
            self.next()

    def startDIT(self):
        #print('Starting DIT')
        self.endOfCharTimeout.deinit()
        self.endOfWordTimeout.deinit()
        self.currentElement = IambicKeyer.DIT
        self.callback(self.currentElement)
        self.callback(IambicKeyer.TONE)
        self.toneTimeout.init(mode=Timer.ONE_SHOT,period=self.unitLength,callback=self.stopTone)
        self.elementTimeout.init(mode=Timer.ONE_SHOT,period=self.unitLength * 2,callback=self.endElement)

    def startDAH(self):
        #print('Starting DAH')
        self.endOfCharTimeout.deinit()
        self.endOfWordTimeout.deinit()
        self.currentElement = IambicKeyer.DAH
        self.callback(self.currentElement)
        self.callback(IambicKeyer.TONE)
        self.toneTimeout.init(mode=Timer.ONE_SHOT,period=self.unitLength * 3,callback=self.stopTone)
        self.elementTimeout.init(mode=Timer.ONE_SHOT,period=self.unitLength * 4,callback=self.endElement)

    def startIAMBIC(self):
        #print('Starting IAMBIC')
        if self.buffer.isEmpty(): # Skip Iambic if there is a state change waiting in the buffer
            if self.currentElement == IambicKeyer.DAH:
                self.startDIT()
            elif self.currentElement == IambicKeyer.DIT:
                self.startDAH()
            else:
                print('WARNING Entering Iambic state without current element already set to DIT or DAH')
        else:
            self.next()

    def startQUIET(self):
        #Sprint('Starting QUIET')
        if self.buffer.isEmpty():
            self.currentElement = None
            self.running = False
        else:
            self.next()
            
    def next(self): # Being here means we need to start playing a tone immediately
        self.running = True
        self.currentState = self.buffer.dequeue()
        self.stateHandler(self.currentState)
    
    async def play(self,text):
        for char in text:
            if char == END_OF_WORD:
                await asyncio.sleep_ms(self.unitLength * 4) # Word space becomes 7 units
            else:
                symbol = charToSymbol(char.upper())
                dits = 0
                dahs = 0
                for element in symbol:
                    if element == DIT:
                        dits += 1
                        self.playDIT()
                    if element == DAH:
                        dahs += 1
                        self.playDAH()
                if dits > 0:
                    await asyncio.sleep_ms(dits * 2 * self.unitLength) # element length plus Inter-character space of 1 unit
                if dahs > 0:
                    await asyncio.sleep_ms(dahs * 4 * self.unitLength) # element length plus Inter-character space of 1 unit
                await asyncio.sleep_ms(self.unitLength * 2) # Intra-character space becomes 3 units

