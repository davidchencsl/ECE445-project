import cv2
import base64
from multiprocessing import Process
import time

'''
def tracking_loop(camera, bbox, frame_base64, track_status):
    def scale_bbox(bbox_shared, size):
        bbox = [b for b in bbox_shared]
        bbox[0] *= size[0]
        bbox[1] *= size[1]
        bbox[2] *= size[0]
        bbox[3] *= size[1]
        return bbox

    INACTIVE = 0
    ACTIVE = 1
    video = cv2.VideoCapture(camera)
    IMG_WIDTH = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    IMG_HEIGHT = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    tracker = cv2.legacy.TrackerCSRT_create()
    while True:
        ret, frame = video.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        if track_status.value == INACTIVE:
            bbox = scale_bbox(bbox, (IMG_WIDTH, IMG_HEIGHT))
            tracker.init(frame, bbox)
            track_status.value = ACTIVE
        elif track_status.value == ACTIVE:
        frame_base64.value = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode("utf-8")
'''

def tracking_loop(camera, bbox, frame_base64, track_status):
    video = cv2.VideoCapture(camera)
    while True:
        ret, frame = video.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        frame_base64.value = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode("utf-8")


class Tracker:
    def __init__(self, bbox_input, frame_base64, track_status, camera=0):
        self.camera = camera
        self.frame_base64 = frame_base64
        self.bbox = bbox_input
        self.track_status = track_status
        self.thread = Process(target=tracking_loop, args=(self.camera, self.bbox, self.frame_base64, self.track_status))
        self.thread.start()

    def stop(self):
        self.thread.terminate()

    def get_frame_base64(self):
        return self.frame_base64.value
