from simple_pid import PID
from autolug.control.motor import Motor
from autolug.control.encoder import Encoder
import Jetson.GPIO as GPIO
import time

ENC1 = 12
ENC2 = 13

def main():
    GPIO.setmode(GPIO.BOARD)
    motor_left = Motor(1)
    motor_right = Motor(2)

    encoder_left = Encoder(1, ENC1)
    encoder_right = Encoder(2, ENC2)

    while True:
        # set speed according to bounding box [m/s]
        motor_left.set_speed(1)
        motor_right.set_speed(1)

        left_speed = encoder_left.get_speed()
        right_speed = encoder_right.get_speed()
        motor_left.update(left_speed)
        motor_right.update(right_speed)


if __name__ == '__main__':
    main()