from simple_pid import PID
from util.helper import clamp

class Controller():
    def __init__(self, motor_left, motor_right, encoder_left, encoder_right):
        self.motor_left = motor_left
        self.motor_right = motor_right
        self.encoder_left = encoder_left
        self.encoder_right = encoder_right
        self.pid = PID(1, 0.0, 0.00, setpoint=0)   


    def update(self, deviation_angle, desired_speed):
        l_speed_obs = self.encoder_left.get_speed()
        r_speed_obs = self.encoder_right.get_speed()
        #print(f"left speed: {left_speed}, right speed: {right_speed}")

        # TODO: set desired speed for each motor
        pid_out = self.pid(deviation_angle)
        l_speed = clamp(desired_speed - pid_out, 0, desired_speed)
        r_speed = clamp(desired_speed + pid_out, 0, desired_speed)

        self.motor_left.set_speed(l_speed)
        self.motor_right.set_speed(r_speed)

        motor_left_output = self.motor_left.update(l_speed_obs)
        motor_right_output = self.motor_right.update(r_speed_obs)
        #print(f"left output: {motor_left_output}, right output: {motor_right_output}")
        return motor_left_output, motor_right_output
