from utime import sleep_ms
from machine import Pin, PWM

__version__ = (0, 2, 0)
class Buzzer:
    
    def __init__(self,pin,freq=600,dutyCycleDivider=1):
        self.pwm = PWM(Pin(pin))
        self.freq = freq
        self.dutyCycleDivider = dutyCycleDivider

    def start(self,freq=None,dutyCycleDivider=None):
        if freq is None:
            freq = self.freq
        if dutyCycleDivider is None:
            dutyCycleDivider = self.dutyCycleDivider
        if freq > 0:
            self.pwm.freq(freq)
            self.pwm.duty_u16(int(round(32768/dutyCycleDivider)))
        else:
            self.pwm.deinit()

    def setFrequency(self,freq):
        self.freq = freq
        
    def setDutyCycleDivider(self,dutyCycleDivider):
        self.dutyCycleDivider = dutyCycleDivider

    def stop(self):
        self.pwm.deinit()

                