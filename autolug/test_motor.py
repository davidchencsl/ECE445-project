from simple_pid import PID
from control.motor import Motor
from control.encoder import Encoder
from control.controller import Controller
from util.parameters import *
import Jetson.GPIO as GPIO
import time
import sys
from smbus2 import SMBus

desired_speed = 1.0
deviation_angle = 45.0

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

    # set speed according to bounding box [m/s]
    motor_left.set_speed(1)
    motor_right.set_speed(1)
    with SMBus(1) as bus:
        while True:
            l_speed_obs = encoder_left.get_speed()
            r_speed_obs = encoder_right.get_speed()
            print(f"left speed: {l_speed_obs}, right speed: {r_speed_obs}")

            l_pwm = motor_left.update(l_speed_obs)
            r_pwm = motor_right.update(r_speed_obs)
            
            update_speed_i2c(bus, l_pwm, r_pwm)
        

if __name__ == '__main__':
    main()