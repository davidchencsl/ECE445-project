import cv2
import base64
from multiprocessing import Process, Value
import time

def tracking_loop_QR(camera, bbox_shared, frame_base64, track_status, deviation_angle):
    video = cv2.VideoCapture(camera)
    while True:
        ret, frame = video.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        # TODO: Add QR code detection here
        frame_base64.value = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode("utf-8")

def tracking_loop(camera, bbox_shared, frame_base64, track_status, deviation_angle):
    def scale_bbox(bbox_shared, size):
        bbox = [b for b in bbox_shared]
        bbox[0] *= size[0]
        bbox[1] *= size[1]
        bbox[2] *= size[0]
        bbox[3] *= size[1]
        return bbox

    def calc_deviation_angle(bbox, size):
        x, y, w, h = bbox
        width, height = size
        return (x - width / 2) / width * 90

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
            bbox = scale_bbox(bbox_shared, (IMG_WIDTH, IMG_HEIGHT))
            tracker.init(frame, bbox)
            track_status.value = ACTIVE
        elif track_status.value == ACTIVE:
            ret, bbox = tracker.update(frame)
            if ret:
                # Draw the bounding box on the frame
                x, y, w, h = map(int, bbox)
                deviation_angle.value = calc_deviation_angle(bbox, (IMG_WIDTH, IMG_HEIGHT))
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            else:
                # Display a message if tracking fails
                cv2.putText(frame, "Tracking failed!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        frame_base64.value = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode("utf-8")



def tracking_loop_debug(camera, bbox, frame_base64, track_status, deviation_angle):
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
        self.deviation_angle = Value('f', 0.0)
        self.thread = Process(target=tracking_loop, args=(self.camera, self.bbox, self.frame_base64, self.track_status, self.deviation_angle))
        self.thread.start()

    def stop(self):
        self.thread.terminate()

    def get_frame_base64(self):
        return self.frame_base64.value
    
    def get_deviation_angle(self):
        return self.deviation_angle.value
