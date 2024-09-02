import cv2
import numpy as np
from moviepy.editor import VideoFileClip

import ImageUtils
from Config import Config


def extractGreenAsAlpha(image):
    # Read the image

    # Convert the image to the HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the range for the green color in HSV
    lower_green = np.array([70,250, 220])
    upper_green = np.array([80, 255, 230])

    # Create a mask that identifies the green areas
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Invert the mask to get the non-green areas
    mask_inv = cv2.bitwise_not(mask)

    alpha_channel = np.zeros(mask.shape, dtype=mask.dtype)
    alpha_channel[mask_inv > 0] = 255
    # Convert the image to BGRA (adding an alpha channel)
    bgra = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    # Set the alpha channel based on the inverted mask
    bgra[:, :, 3] = mask_inv

    return bgra


class LikeAndSub:
    def __init__(self, baseFrame, mixer):
        self.clip = VideoFileClip("assets/likeAndSub.mp4")
        self.curFrame = -1
        self.fps = Config().get("GENERAL", "fps")
        self.startFrame = Config().get("LIKEANDSUB", "startFrame")
        self.mixer = mixer

    def nextFrame(self, frame):
        self.curFrame += 1
        if self.curFrame < self.startFrame:
            return frame
        if self.curFrame - self.startFrame >= self.clip.duration*self.clip.fps:
            return frame
        if self.curFrame == self.startFrame:
            self.mixer.registerClip(self.clip.audio)
        overlayFrame = self.curFrame - self.startFrame

        videoFrame = self.clip.get_frame(overlayFrame / self.fps)
        videoFrame = extractGreenAsAlpha(videoFrame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

        videoFrame = cv2.resize(videoFrame, (531, 300), interpolation=cv2.INTER_AREA)
        videoFrame = cv2.cvtColor(videoFrame, cv2.COLOR_BGR2RGBA)
        frame = ImageUtils.pasteImageRGBA(frame, videoFrame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

        return frame
