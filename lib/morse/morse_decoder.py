from lib.callback_handler import CallBackHandler
from lib.scroll_buffer import ScrollBuffer
from lib.morse.morse_alphabet import DIT,DAH,END_OF_WORD,symbolToChar

__version__ = (0, 1, 0)
class MorseDecoder:

    defaultHandler = {
        'Always': [(print,{})]
    }

    def __init__(self,handler=defaultHandler):
        self.callback = CallBackHandler(handler)
        self.buffer = ScrollBuffer(10)

    def switchHandler(self,handler):
        self.callback = CallBackHandler(handler)
            
    def dit(self):
      self.buffer.enqueue(DIT)
    
    def dah(self):
      self.buffer.enqueue(DAH)

    def endOfChar(self):
      self.callback(symbolToChar(str(self.buffer)))
      self.buffer.clear()
    
    def endOfWord(self):
      self.callback(END_OF_WORD)
    