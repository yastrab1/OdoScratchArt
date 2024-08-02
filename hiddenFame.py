import math

import cv2
import numpy as np
from ultralytics import SAM


def findFirstPointInMaskToStartScraping(maskPoints, direction):
    if direction[1] == 0 and direction[0] == 0:
        raise ValueError()
    angle = 90 if direction[1] < 0 else 270
    if direction[0] != 0:
        angle = math.atan(direction[1]/direction[0])
    inverse = 360-angle
    rotMatrix = np.array([[np.cos(inverse), -np.sin(inverse)],
                             [np.sin(inverse),  np.cos(inverse)]])
    smallestX = math.inf
    index = 0
    for i in range(len(maskPoints)):
        transformedPoint = rotMatrix@maskPoints[i]
        if smallestX > transformedPoint[0]:
            smallestX = transformedPoint[0]
            index = i
    return maskPoints[index]


class HiddenFrame:
    def __init__(self, baseFrame):
        self.frame = cv2.imread("img.png")
        model = SAM("sam2_l.pt")
        model.info()
        result = model("img.png", task='segmentation', device='cuda:0')
        self.maskPoints = result[0].masks.xy
        self.direction = [1,0]
        self.centroids = self.precomputeCentroids()
        self.masks = self.precomputeMasks()
        self.firstPoints = self.precomputeFirstMaskPoints()

    def showCentroids(self):
        for centroid in self.centroids:
            self.frame = cv2.circle(self.frame, (int(centroid[0]), int(centroid[1])), 5, (0, 0, 255), -1)
        cv2.imshow('frame', self.frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def precomputeCentroids(self):
        centroids = []
        for mask in self.maskPoints:
            centroids.append(sum(mask) / len(mask))
        return centroids

    def precomputeMasks(self):
        masks = []

        for mask in self.maskPoints:
            print(mask)
            img = np.zeros(self.frame.shape[:2], np.int8)
            img = cv2.fillPoly(img, pts=np.array([mask], dtype=np.int32), color=255)
            masks.append(img)
        return masks

    def precomputeFirstMaskPoints(self):
        firstMaskPoints = []
        for maskPoints in self.maskPoints:
            firstMaskPoints.append(findFirstPointInMaskToStartScraping(maskPoints, self.direction))
        return firstMaskPoints

    def _showMasks(self):
        for mask in self.masks:
            i = 0
            withBg = self.frame.copy()
            withBg[mask == False] = 255
            cv2.imshow('mask', withBg)
            cv2.imwrite(f"mask{i}.png", withBg)
            cv2.waitKey(0)
        cv2.destroyAllWindows()

    def combineAllMasks(self):
        combined = np.zeros_like(self.frame.shape)
        for mask in self.masks:
            combined[mask] = 255
        return combined
    def nextFrame(self,frame):



HiddenFrame(None)._showMasks()
