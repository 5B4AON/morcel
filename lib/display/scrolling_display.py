from lib.display.writer import Writer
from lib.scroll_buffer import ScrollBuffer
from time import sleep_ms
from lib.display.fonts import fonts

__version__ = (0, 1, 0)

class ScrollingDisplay:
    def __init__(self,oled,fontsize=1,row=0,col=0,lines=1,lineSize=None,fillChar=None):
        self.oled = oled
        self.fontsize = fontsize
        self.row = row
        self.col = col
        self.lines = lines
        self.lineSize = lineSize
        self.setFontParams()
        self.bufLength = self.lineSize * self.lines
        self.fw = Writer(self.oled, self.font, False)
        self.fw.set_clip(True,True,False) # prevent Writer from scrolling when nearing edges
        self.buf = ScrollBuffer(self.bufLength, fillChar)

    def setFontParams(self):
        self.font = fonts.setdefault(self.fontsize, fonts[1])
        if self.lineSize is None:
            self.lineSize = (self.oled.width - self.col) // self.font.max_width()
        max_lines = self.oled.height // self.font.height()
        if self.lines not in range(max_lines + 1): # verify that +1 means max is allowed
            self.lines = 1
        if self.lines == 0:
            self.lines = max_lines
        if self.row + self.font.height() > self.oled.height:
            self.row = self.oled.height - self.font.height()
        if self.col + self.font.max_width() > self.oled.width:
            self.col = self.oled.width - self.font.max_width()

    def _newLine(self,cRow):
        self.fw.set_textpos(self.oled,cRow,self.col)
        for i in range(self.lineSize):
            self.fw.printstring(' ')
        self.fw.set_textpos(self.oled,cRow,self.col)

    def _printMultiline(self):      
        cRow = self.row
        cCol = self.col
        cLine = ''
        for c in str(self.buf):
            cLine = cLine + c
            cCol = cCol + self.font.max_width()
            if cCol + self.font.max_width() >= self.oled.width:
                self.fw.printstring(cLine)
                if cRow + self.font.height() * 2 <= self.oled.height:
                    cRow = cRow + self.font.height()
                    cCol = self.col
                    cLine = ''
                    self._newLine(cRow)
        if not self.buf.isFull():
            self.fw.printstring(cLine)

    def printBuffer(self):
        self.fw.set_textpos(self.oled,self.row,self.col) # set origin
        if self.lines == 1:
            self.fw.printstring(str(self.buf))
        else:
            self._printMultiline()
        self.oled.show()
    
    def clear(self,delay=0):
        if delay > 0:
            for i in range(self.bufLength):
                self.buf.enqueue(' ')
                self.printBuffer()
                sleep_ms(delay)
        else:
            for i in range(self.bufLength):
                self.buf.enqueue(' ')
            self.printBuffer()
        self.buf.clear()
    
    def setPosition(self,row,col):
        self.row = row
        self.col = col
        self.printBuffer()
    
    def _add_character(self,c):
        if self.buf.isFull() and not self.lines == 1:
            for i in range(self.lineSize):
                self.buf.dequeue()
        self.buf.enqueue(c)
    
    def _wordWrap(self,s):
        result = ''
        tokens = s.split()
        spaceLeft = (self.buf.capacity() - self.buf.size()) % self.lineSize
        if spaceLeft == 0:
            spaceLeft = self.lineSize
        for t in tokens:
            if len(t) > spaceLeft:
                if len(t) > self.lineSize:
                    result = result + t
                    if len(s) - spaceLeft > self.lineSize:
                        mod = (len(t) - spaceLeft) % self.lineSize
                        if mod == 0:
                            spaceLeft = self.lineSize
                        else:
                            result = result + ' '
                            spaceLeft = self.lineSize - mod - 1
                    else:
                        if len(t) - spaceLeft == self.lineSize:
                            spaceLeft = self.lineSize
                        else:
                            result = result + ' '
                            spaceLeft = self.lineSize - (len(t) - spaceLeft) - 1
                else:
                    result = result + ' ' * spaceLeft # wrap word here
                    result = result + t
                    if len(t) == self.lineSize:
                        spaceLeft = self.lineSize
                    else:
                        result = result + ' '
                        spaceLeft = self.lineSize - len(t) - 1
            else:
                result = result + t
                if len(t) == spaceLeft:
                    spaceLeft = self.lineSize
                else:
                    result = result + ' '
                    spaceLeft = spaceLeft - len(t) - 1
        return result
    
    def print(self,s,delay=0,wordWrap=False):
        if wordWrap:
            s = self._wordWrap(s)
        if delay > 0:
            for c in s:
                self._add_character(c)
                if c != ' ':
                    self.printBuffer()
                    sleep_ms(delay)
        else:
            for c in s:
                self._add_character(c)
            self.printBuffer()

    def println(self,s,delay=0,wordWrap=False):
        self.print(s,delay)
        padding = (self.buf.capacity() - self.buf.size()) % self.lineSize
        if padding > 0:
            self.print(' ' * padding,0)