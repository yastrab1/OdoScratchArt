import cv2


class BaseFrame:
    def __init__(self,firstFrame,mixer):
        self.img = cv2.imread("img.png")
        self.curFrame = 0

    def baseImg(self,frame):
        self.curFrame +=1
        if self.curFrame == 500:
            raise StopIteration
        return self.img