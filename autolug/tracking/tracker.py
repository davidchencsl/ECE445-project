import cv2
import base64
from multiprocessing import Process, Value
import time

import numpy as np
'''
def register_owner(owner_id):
    img = pyqrcode.create(owner_id)
    img.png(owner_id + '.png', scale=8)
    img.show()
'''

def tracking_loop_QR(camera, bbox_shared, frame_base64, track_status, deviation_angle, desired_speed, max_speed, owner_id="abcd"):
    def calc_deviation_angle(bbox, size):
        x, y = bbox
        width, height = size
        return (x - width / 2) / width * 45
    
    def tilt_correction(frame, angle):
        angle = np.deg2rad(angle)
        height, width = frame.shape[:2]
        src_points = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
        dst_points = np.float32([
        [0, height * np.sin(angle)], 
        [width, height * np.sin(angle)], 
        [0, height], 
        [width, height]
    ])
        perspective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        return cv2.warpPerspective(frame, perspective_matrix, (width, height))

    decoder = cv2.QRCodeDetector()
    vid = cv2.VideoCapture(camera)
    
    IMG_WIDTH = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    IMG_HEIGHT = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    LOST_PERIOD = 5
    track_status.value = 0
    found_obj = False

    # iterative variables
    lost_count = 0
    cur_dev = 0

    while True:
        ret, frame = vid.read()
        #frame = cv2.rotate(frame, cv2.ROTATE_180)
        frame = tilt_correction(frame, 0)
        # frame preprocess
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = np.ones((3, 3), np.uint8)
        thresh = cv2.dilate(thresh, kernel, iterations=1)
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        bboxes = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            xmin, ymin, width, height = cv2.boundingRect(cnt)
            extent = area / (width * height)
        
            # filter non-rectangular objects and small objects
            if (extent > np.pi / 4) and (area > 2000):
                bboxes.append((xmin, ymin, xmin + width, ymin + height))

        for xmin, ymin, xmax, ymax in bboxes:
            roi = frame[ymin:ymax, xmin:xmax]
            data, _, _ = decoder.detectAndDecode(roi)
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            print(data)
            points = [[xmin,ymin],[xmin,ymax],[xmax,ymin],[xmax,ymax]]
            if data == owner_id:
                found_obj = True
                center = [int(xmin+xmax/2), int(ymin+ymax)]
                
                # calculate deviation angle
                cur_dev = calc_deviation_angle(center, (IMG_WIDTH, IMG_HEIGHT))

                # draw boudning box around the owner QR code
                for i in range(len(points)):
                    pt1 = [int(val) for val in points[i]]
                    pt2 = [int(val) for val in points[(i + 1) % 4]]
                    pt1 = tuple(pt1)
                    pt2 = tuple(pt2)
                    cv2.line(frame, pt1, pt2, color=(255, 0, 0), thickness=3)

        if found_obj:
            # tracker found the owner
            found_obj = False
            deviation_angle.value = cur_dev 
            desired_speed.value = max_speed.value
            track_status.value = 1
            lost_count = 0
        else:
            # owner lost!
            lost_count += 1
            if lost_count > LOST_PERIOD:
                track_status.value = 0

        cur_dev = 0
        frame_base64.value = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode("utf-8")

def tracking_loop(camera, bbox_shared, frame_base64, track_status, deviation_angle, desired_speed, max_speed):
    def scale_bbox(bbox_shared, size):
        bbox = [b for b in bbox_shared]
        bbox[0] *= size[0]
        bbox[1] *= size[1]
        bbox[2] *= size[0]
        bbox[3] *= size[1]
        x = (bbox[0] + bbox[2])/2 - 180
        y = (bbox[1] + bbox[3])/2 - 180
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        return (x,y,w,h)

    def calc_deviation_angle(bbox, size):
        x, y, w, h = bbox
        width, height = size
        return (x - width / 2) / width * 90

    INACTIVE = 0
    ACTIVE = 1
    HAS_BBOX = 2
    video = cv2.VideoCapture(camera)
    IMG_WIDTH = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    IMG_HEIGHT = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    tracker = cv2.TrackerCSRT_create()
    init = False
    while True:
        ret, frame = video.read()
        #frame = cv2.rotate(frame, cv2.ROTATE_180)
        if track_status.value == HAS_BBOX:
            init = True
            track_status.value = INACTIVE
        if init:
            if track_status.value == INACTIVE:
                bbox = scale_bbox(bbox_shared, (IMG_WIDTH, IMG_HEIGHT))
                tracker.clear()
                tracker = cv2.TrackerCSRT_create()
                tracker.init(frame, bbox)
                track_status.value = ACTIVE
            elif track_status.value == ACTIVE:
                ret, bbox = tracker.update(frame)
                if ret:
                    # Draw the bounding box on the frame
                    x, y, w, h = map(int, bbox)
                    deviation_angle.value = calc_deviation_angle(bbox, (IMG_WIDTH, IMG_HEIGHT))
                    desired_speed.value = 0.5
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                else:
                    # Display a message if tracking fails
                    cv2.putText(frame, "Tracking failed!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        frame_base64.value = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode("utf-8")



def tracking_loop_debug(camera, bbox, frame_base64, track_status, deviation_angle, desired_speed, max_speed):
    video = cv2.VideoCapture(camera)
    while True:
        ret, frame = video.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        frame_base64.value = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode("utf-8")


class Tracker:
    def __init__(self, bbox_input, frame_base64, track_status, max_speed, camera=0):
        self.camera = camera
        self.frame_base64 = frame_base64
        self.bbox = bbox_input
        self.track_status = track_status
        self.deviation_angle = Value('f', 0.0)
        self.desired_speed = Value('f', 0.0)
        self.max_speed = max_speed
        self.thread = Process(target=tracking_loop_QR, args=(self.camera, self.bbox, self.frame_base64, self.track_status, self.deviation_angle, self.desired_speed, self.max_speed))
        self.thread.start()

    def stop(self):
        self.thread.terminate()

    def get_frame_base64(self):
        return self.frame_base64.value
    
    def get_deviation_angle(self):
        return self.deviation_angle.value
    
    def get_desired_speed(self):
        return self.desired_speed.value
