import cv2

class Tracker:
    def __init__(self, camera):
        pass
    
    def get_frame_base64(self):
        return base64.b64encode(cv2.imencode('.jpg', self.frame)[1]).decode()