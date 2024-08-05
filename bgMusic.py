import os
import random

from moviepy.audio.io.AudioFileClip import AudioFileClip

from AudioMixer import AudioMixer

class BgMusic:
    def __init__(self, baseFrame,mixer:AudioMixer):
        self.mixer = mixer
        self.clips = []
        self.curFrame = 0
        self.curClip:AudioFileClip = None
        self.lastClipFrame = 0
        self.loadMusic()

    def loadMusic(self):
        for file in os.listdir("audio"):
            self.clips.append(AudioFileClip(os.path.join("audio", file)))

    def nextFrame(self,frame):
        if self.curFrame == 0:
            self.curClip = random.choice(self.clips)
            self.mixer.registerClip(self.curClip)
            self.lastClipFrame = self.curFrame
        if self.curClip.fps*self.curClip.duration + self.lastClipFrame == len(self.clips):
            self.curClip = random.choice(self.clips)
            self.mixer.registerClip(self.curClip)
            self.lastClipFrame = self.curFrame
        self.curFrame += 1
        return frame