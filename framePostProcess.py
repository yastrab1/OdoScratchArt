import cv2


class FramePostProcess:
    def __init__(self,baseFrame,mixer):
        pass
    def nextFrame(self,frame):
        frame = frame[:, :, :3]
        return frame