﻿from moviepy.audio.AudioClip import AudioClip, CompositeAudioClip


class AudioMixer:
    def __init__(self, fps=30):
        self.clips = []
        self.fps = fps
        self.currentFrame = 0

    def finishFrame(self):
        self.currentFrame += 1

    def registerClip(self, clip: AudioClip):
        print("Clipped",self.currentFrame)
        clip = clip.set_start(self.currentFrame/ self.fps)
        self.clips.append(clip)

    def getFullClip(self):
        for clip in self.clips:
            print(clip.duration, clip.start)
        return CompositeAudioClip(self.clips)
