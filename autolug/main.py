from simple_pid import PID
from control.motor import Motor
from control.encoder import Encoder
import Jetson.GPIO as GPIO
import time
from smbus2 import SMBus



ENC1 = 12
ENC2 = 13

I2C_ADDR = 0x08

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
    motor_left.set_speed(0.5)
    motor_right.set_speed(0.5)

    with SMBus(1) as bus:
        while True:
            left_speed = encoder_left.get_speed()
            right_speed = encoder_right.get_speed()
            print(f"left speed: {left_speed}, right speed: {right_speed}")
            motor_left_output = motor_left.update(left_speed)
            motor_right_output = motor_right.update(right_speed)
            print(f"left output: {motor_left_output}, right output: {motor_right_output}")
            update_speed_i2c(bus, motor_left_output, motor_right_output)


if __name__ == '__main__':
    main()