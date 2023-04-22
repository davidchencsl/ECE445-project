from dataclasses import dataclass
from simple_pid import PID
from control.motor import Motor
from control.encoder import Encoder
from control.controller import Controller
from control.tof import TOF
from util.parameters import *
import Jetson.GPIO as GPIO
import time
import threading
from multiprocessing import Process, Value
from smbus2 import SMBus
from flask import Flask, request
import json
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


desired_speed = Value('f', 0.0)
deviation_angle = Value('f', 0.0)
l_speed = Value('f', 0.0)
r_speed = Value('f', 0.0)
l_pwm = Value('i', 0)
r_pwm = Value('i', 0)
distance = Value('f', 0.0)
stop_flag = False

app = Flask(__name__)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return json.dumps({'l_speed': l_speed.value,
                        'r_speed': r_speed.value,
                        'l_pwm': l_pwm.value,
                        'r_pwm': r_pwm.value,
                        'distance': distance.value,
                       })

@app.route('/api/controls', methods=['POST'])
def set_controls():
    data = request.json
    desired_speed.value = data['desired_speed']
    deviation_angle.value = data['deviation_angle']
    return 'OK'
    

def keyboard_thread():
    global stop_flag
    while True:
        key = input()
        if key == 'q':
            stop_flag = True
            break
        elif key.startswith('a'):
            deviation_angle.value = float(key[1:])
            print(f"deviation angle: {deviation_angle}")
        elif key.startswith('s'):
            desired_speed.value = float(key[1:])
            print(f"desired speed: {desired_speed}")

def update_speed_i2c(bus, speed_left, speed_right):
    bus.write_byte(I2C_ADDR, speed_left)
    bus.write_byte(I2C_ADDR, speed_right)
    return bus.read_byte(I2C_ADDR), bus.read_byte(I2C_ADDR)

def controller_loop(controller, i2c_bus):
    l_speedv, r_speedv, l_pwmv, r_pwmv, distancev = controller.update(deviation_angle.value, desired_speed.value)
    l_speed.value = l_speedv
    r_speed.value = r_speedv
    l_pwm.value = l_pwmv
    r_pwm.value = r_pwmv
    distance.value = distancev
    print(f"l_speed: {l_speedv}, r_speed: {r_speedv}, l_pwm: {l_pwmv}, r_pwm: {r_pwmv}, distance: {distancev}")
    update_speed_i2c(i2c_bus, l_pwmv, r_pwmv)

def main():
    GPIO.setmode(GPIO.BOARD)
    motor_left = Motor(1)
    motor_right = Motor(2)

    encoder_left = Encoder(1, ENC1)
    encoder_right = Encoder(2, ENC2)

    tof = TOF(1, TOF_IN, TOF_OUT)

    controller = Controller(motor_left, motor_right, encoder_left, encoder_right, tof, safety_distance=0.5)

    # set speed according to bounding box [m/s]
    motor_left.set_speed(0)
    motor_right.set_speed(0)

    bus = SMBus(1)
    threading.Thread(target=keyboard_thread).start()
    server = Process(target=app.run, args=('0.0.0.0', 6969))
    server.start()

    while True:
        controller_loop(controller, bus)
        if stop_flag:
            break
        time.sleep(0.05)
    
    print("Cleaning up...")
    update_speed_i2c(bus, 0, 0)
    encoder_left.stop()
    encoder_right.stop()
    tof.stop()
    bus.close()
    server.terminate()
    GPIO.cleanup()


if __name__ == '__main__':
    main()