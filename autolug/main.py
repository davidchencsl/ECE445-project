from simple_pid import PID
from control.motor import Motor
from control.encoder import Encoder
from control.controller import Controller
from util.parameters import *
import Jetson.GPIO as GPIO
import time
from smbus2 import SMBus

desired_speed = 1.0
deviation_angle = 0.0

def update_speed_i2c(bus, speed_left, speed_right):
    bus.write_byte(I2C_ADDR, speed_left)
    bus.write_byte(I2C_ADDR, speed_right)
    return bus.read_byte(I2C_ADDR), bus.read_byte(I2C_ADDR)


def main():
    GPIO.setmode(GPIO.BOARD)
    motor_left = Motor(1)
    motor_right = Motor(2)

    encoder_left = Encoder(1, ENC1)
    encoder_right = Encoder(2, ENC2)

    controller = Controller(motor_left, motor_right, encoder_left, encoder_right)

    # set speed according to bounding box [m/s]
    motor_left.set_speed(0.5)
    motor_right.set_speed(0.5)


    with SMBus(1) as bus:
        while True:
        
            l_pwm, r_pwm = controller.update(deviation_angle, desired_speed)
            print(f"left pwm: {l_pwm}, right pwm: {r_pwm}")
            update_speed_i2c(bus, l_pwm, r_pwm)


if __name__ == '__main__':
    main()