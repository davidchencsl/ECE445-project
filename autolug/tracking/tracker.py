import cv2
import base64
from multiprocessing import Process, Manager, Value
from ctypes import c_char_p
import time

def sample_loop(camera, frame_base64):
    video = cv2.VideoCapture(camera)
    while True:
        ret, frame = video.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        frame_base64.value = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode("utf-8")

class Tracker:
    def __init__(self, camera=0):
        self.camera = camera
        self.period = 0.05
        self.manager = Manager()
        self.frame_base64 = self.manager.Value(c_char_p, "")
        self.thread = Process(target=sample_loop, args=(self.camera, self.frame_base64))
        self.thread.start()

    def stop(self):
        self.thread.terminate()

    def get_frame_base64(self):
        return self.frame_base64.value
