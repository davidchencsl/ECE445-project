import Jetson.GPIO as GPIO
import time

class Encoder():
    def __init__(self, id, pin):
        self.id = id
        self.pin = pin
        self.count = 0
        self.prev_count = 0
        self.curr_count = 0
        self.prev_time = None
        self.curr_time = None

        GPIO.setup(self.pin, GPIO.IN)
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.handler)
    
    def handler(self, channel):
        self.count += 1
    
    def get_speed(self):
        if self.prev_time is None:
            self.prev_time = time.time()
            self.prev_count = self.count
            return 0.0
        
        self.curr_time = time.time()
        self.curr_count = self.count
        speed = (self.curr_count - self.prev_count) / (self.curr_time - self.prev_time)
        
        self.prev_time = self.curr_time
        self.prev_count = self.curr_count
        return speed

