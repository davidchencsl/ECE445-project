import Jetson.GPIO as GPIO
import time

from autolug.util.parameters import DISTANCE_PER_PULSE

class Encoder():
    def __init__(self, id, pin):
        self.id = id
        self.pin = pin
        self.trigger_time = None

        GPIO.setup(self.pin, GPIO.IN)
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.handler)
    
    def handler(self, channel):
        self.trigger_time = time.time()
    
    def get_speed(self):
        # 16 pulses per revolution
        dist = DISTANCE_PER_PULSE
        if self.trigger_time is None:
            return 0
        else:
            return dist/(time.time() - self.trigger_time)

