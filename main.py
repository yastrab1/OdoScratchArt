import cv2
import numpy as np
from moviepy.video.io.VideoFileClip import VideoFileClip

from Pipeline import Pipeline
from AudioMixer import AudioMixer


def generate_video_from_frames(pipeline, output_file, fps=30):
    """
    Generates a video from in-memory stored frames.

    :param frames: List of frames (numpy arrays)
    :param output_file: Output video file path (e.g., 'output.mp4')
    :param fps: Frames per second
    """
    frame0 = pipeline.baseFrame

    # Get frame dimensions
    height, width, layers = frame0.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4 files
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    # out.write(frame0)
    for frame in pipeline:
        out.write(frame)

    out.release()

    print(f"Video saved as {output_file}")


if __name__ == "__main__":
    fps = 30
    mixer = AudioMixer(fps)
    pipeline = Pipeline(mixer)
    pipeline.loadFromConfig()

    generate_video_from_frames(pipeline, 'output.mp4')
    # audio = mixer.getFullClip()
    # video = VideoFileClip('output.mp4')
    # video.audio = audio.subclip(0,video.duration)
    # video.write_videofile('output.mp4')
