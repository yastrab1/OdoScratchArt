import random
import os
from dotenv.main import load_dotenv
import cv2
from PIL import Image
import requests
import ImageUtils

import io


class BaseFrame:
    def __init__(self,firstFrame,mixer):
        self.img = ImageUtils.pilToCv2(self.generateImage(self.generatePrompt()))
        cv2.imshow("Skbidi",self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
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

    def generateImage(self,prompt):
        load_dotenv(verbose=True)
        os.environ["HUGGING_API"] = "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"

        payload = {
            "inputs": prompt,
        }

        API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
        headers = {"Authorization": f"Bearer {os.getenv("HUGGING_API")}"}

        response = requests.post(API_URL, headers=headers, json=payload)

        return Image.open(io.BytesIO(response.content))


    def baseImg(self,frame):
        self.curFrame +=1
        return self.img