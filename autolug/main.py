from simple_pid import PID
from control.motor import Motor
from control.encoder import Encoder
from control.controller import Controller
from util.parameters import *
import Jetson.GPIO as GPIO
import time
import threading
from multiprocessing import Process
from smbus2 import SMBus
from flask import Flask, request
import json
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

desired_speed = 1.0
deviation_angle = 0.0
stop_flag = False
app = Flask(__name__)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return json.dumps({'l_speed': 0.5,
                        'r_speed': 0.5,
                        'l_pwm': 129,
                        'r_pwm': 129,
                        'distance': 0.5,
                       })

@app.route('/api/controls', methods=['POST'])
def set_controls():
    data = request.json
    print(data)
    return 'OK'

def keyboard_thread():
    global stop_flag
    global desired_speed
    global deviation_angle
    while True:
        key = input()
        if key == 'q':
            stop_flag = True
            break
        elif key.startswith('a'):
            deviation_angle = float(key[1:])
            print(f"deviation angle: {deviation_angle}")
        elif key.startswith('s'):
            desired_speed = float(key[1:])
            print(f"desired speed: {desired_speed}")

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

    bus = SMBus(1)
    threading.Thread(target=keyboard_thread).start()
    server = Process(target=app.run, args=('0.0.0.0', 6969))
    server.start()

    while True:
    
        l_pwm, r_pwm = controller.update(deviation_angle, desired_speed)
        print(f"left pwm: {l_pwm:03}, right pwm: {r_pwm:03}, deviation angle: {deviation_angle:03}, desired speed: {desired_speed:03}")
        update_speed_i2c(bus, l_pwm, r_pwm)
        
        if stop_flag:
            break
        time.sleep(0.05)
    
    print("Cleaning up...")
    update_speed_i2c(bus, 0, 0)
    encoder_left.stop()
    encoder_right.stop()
    bus.close()
    server.terminate()
    GPIO.cleanup()


if __name__ == '__main__':
    main()