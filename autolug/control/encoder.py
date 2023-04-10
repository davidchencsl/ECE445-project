import Jetson.GPIO as GPIO
import time

from autolug.util.parameters import DISTANCE_PER_PULSE

class Encoder():
    def __init__(self, id, pin):
        self.id = id
        self.pin = pin
        self.last_pulse = None
        self.prev_pulse = None

        GPIO.setup(self.pin, GPIO.IN)
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.handler)
    
    def handler(self, channel):
        self.prev_pulse = self.last_pulse
        self.last_pulse = time.time()
    
    def get_speed(self):
        # 16 pulses per revolution
        if self.prev_pulse is None:
            return 0
        else:
            return DISTANCE_PER_PULSE/(self.last_pulse - self.prev_pulse)

