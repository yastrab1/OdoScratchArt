import math

import cv2
import numpy
import numpy as np
from PIL import ImageFilter
from ultralytics import SAM

from ImageUtils import cv2ToPil, pilToCv2


def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def findFirstPointInMaskToStartScraping(maskPoints, angle):
    inverse = 360 - angle
    rotMatrix = np.array([[np.cos(inverse), -np.sin(inverse)],
                          [np.sin(inverse), np.cos(inverse)]])
    smallestX = math.inf
    biggestX = -math.inf
    smallestIndex = 0
    biggestIndex = 0
    for i in range(len(maskPoints)):
        transformedPoint = rotMatrix @ maskPoints[i]
        if smallestX > transformedPoint[0]:
            smallestX = transformedPoint[0]
            smallestIndex = i
        if biggestX < transformedPoint[0]:
            biggestX = transformedPoint[0]
            biggestIndex = i
    return numpy.array(maskPoints[smallestIndex], np.int32), numpy.array(maskPoints[biggestIndex], np.int32)


def calculateAngleFromDirection(direction):
    if direction[1] == 0 and direction[0] == 0:
        raise ValueError()
    angle = 90 if direction[1] < 0 else 270
    if direction[0] != 0:
        angle = math.atan(direction[1] / direction[0]) * 180 / math.pi
    if direction[0] >= 0 and direction[1] <= 0:
        angle += 90
    if direction[0] <= 0 and direction[1] <= 0:
        angle += 180
    if direction[0] <= 0 and direction[1] >= 0:
        angle += 270
    return angle


class HiddenFrame:
    def __init__(self, baseFrame,mixer):
        self.frame = baseFrame
        model = SAM("sam2_l.pt")
        model.info()
        result = model(baseFrame, task='segmentation', device='cuda:0')
        self.hiddenImage = self.makeHiddenImage()
        self.maskPoints = result[0].masks.xy
        self.direction = normalize(np.array([1, 1]))
        self.directionAngle = int(calculateAngleFromDirection(self.direction))
        self.masks = [Mask(mask, self.frame.shape, self.directionAngle) for mask in self.maskPoints]

        self.sortMasksByDistanceToCenter()
        self.finalMask = np.zeros(self.frame.shape[:2], np.uint8)
        self.currentMask = self.masks[0]
        self.currentRectHeight = 1
        self.currentMaskIndex = 0

    def addDefaultMask(self):
        combined = np.zeros(self.frame.shape[:2], np.uint8)
        for mask in self.masks:
            combined[mask.mask == 255] = 255
        self.masks.append(Mask(combined, self.frame.shape, self.directionAngle))

    def makeHiddenImage(self):
        pilimg = cv2ToPil(self.frame)
        scrapedGrayscale = pilimg.convert("RGBA")
        image = scrapedGrayscale.filter(ImageFilter.FIND_EDGES).convert("RGBA")
        return pilToCv2(image)

    def showCentroids(self):
        for mask in self.masks:
            self.frame = cv2.circle(self.frame, (int(mask.centroid[0]), int(mask.centroid[1])), 5, (0, 0, 255), -1)
        cv2.imshow('frame', self.frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def _showMasks(self):
        for mask in self.masks:
            i = 0
            withBg = self.frame.copy()
            withBg[mask.mask == False] = 255
            withBg = cv2.circle(withBg, mask.firstMaskPoint, 5, (0, 0, 255), -1)
            withBg = cv2.circle(withBg, mask.lastMaskPoint, 5, (0, 255, 0), -1)
            cv2.imshow('mask', withBg)
            cv2.imwrite(f"mask{i}.png", withBg)
            cv2.waitKey(0)
        cv2.destroyAllWindows()

    def sortMasksByDistanceToCenter(self):
        center = [self.frame.shape[1] // 2, self.frame.shape[0] // 2]
        self.masks.sort(key=lambda mask: mask.centroidDistanceTo(center), reverse=True)

    def nextFrame(self, frame):
        self.currentRectHeight += 1

        line = self.makeLine()

        # testing = line.copy()
        # testing[self.currentMask.mask == 255] = 255
        # for mask in self.masks:
        #     testing = cv2.circle(testing,mask.firstMaskPoint,5,50,-1)
        #     testing = cv2.circle(testing,mask.lastMaskPoint,5,125,-1)
        #
        # cv2.imshow("mask",testing)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        self.finalMask[(line == 255) & (self.currentMask.mask == 255)] = 255

        merged_image = np.zeros_like(self.frame)

        merged_image[self.finalMask == 255] = frame[self.finalMask == 255]
        merged_image[self.finalMask == 0] = self.hiddenImage[self.finalMask == 0]

        if self.isWholeMaskFilled(line):
            self.currentMaskIndex += 1
            if self.currentMaskIndex >= len(self.masks):
                raise StopIteration
            self.currentRectHeight = 1
            self.currentMask = self.masks[self.currentMaskIndex]

        return merged_image

    def isWholeMaskFilled(self, line):
        return np.count_nonzero(self.currentMask.mask & line) == 0

    def makeLine(self):
        line = np.zeros(self.frame.shape[:2], np.uint8)
        t_values = np.linspace(0, sum(self.frame.shape) * 2, sum(self.frame.shape) * 2)
        divided = self.direction[0] / self.direction[1]
        initialX = (self.currentMask.firstMaskPoint[0] - divided * self.currentMask.firstMaskPoint[1] +
                    math.copysign(1, self.direction[1]) * self.currentRectHeight)
        initialY = 0
        # Generate x and y coordinates of the line
        x_values = initialX + t_values * self.direction[0]
        y_values = initialY + t_values * self.direction[1]
        # Round and convert to integer indices
        x_indices = np.round(x_values).astype(int)
        y_indices = np.round(y_values).astype(int)
        valid_indices = (
                (x_indices >= 0) & (x_indices < line.shape[1]) &
                (y_indices >= 0) & (y_indices < line.shape[0])
        )
        x_indices = x_indices[valid_indices]
        y_indices = y_indices[valid_indices]
        # Set the line points to 255
        line[y_indices, x_indices] = 255
        return line


class Mask:
    def __init__(self, points, imgShape, directionAngle):
        self.points = points
        self.mask = self.precomputeMask(imgShape)
        self.centroid = self.precomputeCentroid()
        self.firstMaskPoint, self.lastMaskPoint = findFirstPointInMaskToStartScraping(self.points, directionAngle)

    def precomputeMask(self, imgShape):
        img = np.zeros(imgShape[:2], np.uint8)
        img = cv2.fillPoly(img, pts=np.array([self.points], dtype=np.int32), color=255)

        return img

    def precomputeCentroid(self):
        centroid = sum(self.points) / len(self.points)
        return centroid

    def centroidDistanceTo(self, point):
        return np.linalg.norm(self.centroid - point)
