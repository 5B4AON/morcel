
# Implementation of a Circular Buffer which allows
# additions when full by overwriting the oldest item

__version__ = (0, 1, 0)
class ScrollBuffer(object):

    def __init__(self, capacity=10, fillObj=None):
        self._capacity = capacity
        self._queue = [fillObj] * capacity
        self._head = 0
        if fillObj is not None:
            self._tail = capacity - 1
            self._size = capacity
        else:
            self._tail = -1
            self._size = 0

    def enqueue(self, item):
        if self.isFull():
            self.dequeue()
        self._tail = (self._tail + 1) % self._capacity
        self._queue[self._tail] = item
        self._size = self._size + 1

    def dequeue(self):
        if self.isEmpty():
            raise IndexError("Buffer is empty, unable to dequeue")
        item = self._queue[self._head]
        self._head = (self._head + 1) % self._capacity
        self._size = self._size - 1
        return item
    
    def clear(self):
        self._head = 0
        self._tail = -1
        self._size = 0        

    def __str__(self):
        s = ""
        index = self._head
        for i in range(self._size):
            s = s + str(self._queue[index])
            index = (index + 1) % self._capacity
        return s

    def lastIndexOf(self,s):
        result = -1
        index = self._head
        for i in range(self._size):
            if str(self._queue[index]) == s:
                result = i
            index = (index + 1) % self._capacity
        return result

    def size(self):
        return self._size
    
    def capacity(self):
        return self._capacity

    def isEmpty(self):
        return self._size == 0

    def isFull(self):
        return self._size == self._capacity

    def peek(self):
        if self._size > 0:
            return self._queue[self._head]
        else:
            return None
    
    def peekTail(self):
        if self._size > 0:
            return self._queue[self._tail]
        else:
            return None
