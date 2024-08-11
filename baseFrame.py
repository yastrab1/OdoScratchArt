import random

import cv2
from PIL import Image

import ImageUtils


class BaseFrame:
    def __init__(self,firstFrame,mixer):
        self.img = ImageUtils.pilToCv2(Image.open("test.webp"))
        self.curFrame = 0

    def generatePrompt(self):
        ponies = [
            "a wisteria-colored pony with a horn and wings and short hair",
            "an olden-amber colored pony with apples on his leg and casino-lights colored hair."
        ]
        states = [
            "running",
            "sitting",
            "having fun"
        ]

        prompt = "Generate a wide aspect ratio cartoon style image with:"
        amountOfPonies = random.randint(1, len(ponies))
        promptPony = random.sample(ponies,amountOfPonies)
        promptState = random.sample(states,amountOfPonies)
        prompt += " " + ", ".join([f"{p} {s}" for p, s in zip(promptPony, promptState)])

        return prompt


    def baseImg(self,frame):
        self.curFrame +=1
        return self.img