import cv2
import numpy as np

from ImageUtils import pasteImageRGBA, pasteMaskOnMask


class BouncingScratcher:
    def __init__(self, baseFrame, mixer):
        self.scrapedImage = baseFrame
        self.finalMask = np.zeros(self.scrapedImage.shape[:2], np.uint8)
        self.scratcher = cv2.imread("assets/scratcher.png", cv2.IMREAD_UNCHANGED)
        self.currentScratcherPos = np.array([baseFrame.shape[1] // 2, baseFrame.shape[0] // 2])
        self.scratcherDirection = np.array([-1, -1])
        self.scratcherDirection = self.scratcherDirection/np.linalg.norm(self.scratcherDirection)
        self.scratcherSpeed = 5
        self.scratcherMask = self.scratcher[:,:,3]
        self.scratcherMask = np.where(self.scratcherMask > 0, 255, 0).astype(np.  uint8)

    def nextFrame(self, frame):
        self.moveScratcher()

        self.finalMask = pasteMaskOnMask(self.finalMask, self.scratcherMask, *self.currentScratcherPos)

        frame[self.finalMask == 255] = self.scrapedImage[self.finalMask == 255]

        frame = pasteImageRGBA(frame, self.scratcher, self.currentScratcherPos)

        return frame

    def flipScratcher(self,axis):
        self.scratcher = cv2.flip(self.scratcher, axis)
        self.scratcherMask = cv2.flip(self.scratcherMask, axis)

    def moveScratcher(self):
        frameH,frameW = self.scrapedImage.shape[:2]
        scratcherH,scratcherW = self.scratcher.shape[:2]
        self.currentScratcherPos += (self.scratcherDirection*self.scratcherSpeed).astype(np.int32)
        nextPos = self.currentScratcherPos + (self.scratcherDirection*self.scratcherSpeed).astype(np.int32)
        if (nextPos[0]+scratcherW > frameW) or (nextPos[0] < 0):
            self.scratcherDirection[0] *= -1
            self.flipScratcher(1)
        if (nextPos[1]+scratcherH > frameH) or (nextPos[1] < 0):
            self.scratcherDirection[1] *= -1
            self.flipScratcher(0)