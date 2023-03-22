from simple_pid import PID
import Jetson.GPIO as GPIO

def Motor():
    def __init__(self, id):
        self.id = id
        self.target_speed = 0
        self.current_speed = 0

        self.pid = PID(1, 0.1, 0.05, setpoint=0)
    
    def set_speed(self, speed):
        self.target_speed = speed
        self.pid.setpoint = speed
    
    def update(self, current_speed):
        self.current_speed = current_speed
        output = self.pid(current_speed)
        print(f"Motor {self.id} pid: {output}")
        # TODO: Send output through I2C to motor driver

