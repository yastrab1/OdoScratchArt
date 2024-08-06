import cv2
import numpy as np


def pasteImageRGBA(back, front, x, y):
    # Get the dimensions of the foreground image
    fh, fw, fc = front.shape

    # Extract the alpha channel from the foreground image
    alpha_foreground = front[:, :, 3] / 255.0
    alpha_background = 1.0 - alpha_foreground

    # Loop over the alpha channels and combine the images
    for c in range(0, 3):
        back[y:y + fh, x:x + fw, c] = (alpha_foreground * front[:, :, c] +
                                       alpha_background * back[y:y + fh, x:x + fw, c])
    return back


def pasteMaskOnMask(back, front, x, y):
    fh, fw = front.shape

    alpha_foreground = front[:, :,]
    alpha_background = 1.0 - alpha_foreground

    back[y:y + fh, x:x + fw] = front*alpha_foreground + alpha_background*back[y:y + fh, x:x + fw]
    return back


class BouncingScratcher:
    def __init__(self, baseFrame, mixer):
        self.scrapedImage = baseFrame
        self.finalMask = np.zeros(self.scrapedImage.shape[:2], np.uint8)
        self.scratcher = cv2.imread("scratcher.png", cv2.IMREAD_UNCHANGED)
        self.currentScratcherPos = np.array([baseFrame.shape[1] // 2, baseFrame.shape[0] // 2])
        self.scratcherDirection = np.array([1, 1])
        self.scratcherDirection = self.scratcherDirection/np.linalg.norm(self.scratcherDirection)
        self.scratcherSpeed = 5
        self.scratcherMask = self.scratcher[:,:,3]
        self.scratcherMask = np.where(self.scratcherMask > 0, 255, 0).astype(np.  uint8)

    def nextFrame(self, frame):
        self.moveScratcher()

        self.finalMask = pasteMaskOnMask(self.finalMask, self.scratcherMask, *self.currentScratcherPos)

        frame[self.finalMask == 255] = self.scrapedImage[self.finalMask == 255]

        frame = pasteImageRGBA(frame, self.scratcher, *self.currentScratcherPos)

        return frame

    def moveScratcher(self):
        frameH,frameW = self.scrapedImage.shape[:2]
        scratcherH,scratcherW = self.scratcher.shape[:2]
        self.currentScratcherPos += (self.scratcherDirection*self.scratcherSpeed).astype(np.int32)
        nextPos = self.currentScratcherPos + (self.scratcherDirection*self.scratcherSpeed).astype(np.int32)
        print(self.currentScratcherPos,frameW,frameH,)
        if (nextPos[0]+scratcherW > frameW) or (nextPos[0] < 0):
            self.scratcherDirection[0] *= -1
            print("Bounmced")
        if (nextPos[1]+scratcherH > frameH) or (nextPos[1] < 0):
            self.scratcherDirection[1] *= -1
            print("Bounmced")