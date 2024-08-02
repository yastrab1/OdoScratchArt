import cv2
import numpy as np
from Pipeline import Pipeline
def generate_video_from_frames(pipeline, output_file, fps=30):
    """
    Generates a video from in-memory stored frames.

    :param frames: List of frames (numpy arrays)
    :param output_file: Output video file path (e.g., 'output.mp4')
    :param fps: Frames per second
    """
    frame0 = pipeline.__next__()

    # Get frame dimensions
    height, width, layers = frame0.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4 files
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    out.write(frame0)
    for frame in pipeline:
        out.write(frame)

    out.release()
    print(f"Video saved as {output_file}")
curFrame = 0
def next(frame):
    global curFrame
    curFrame = curFrame + 1
    if curFrame == 1000:
        raise StopIteration
    return np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
# Example usage
if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.loadFromConfig()


    generate_video_from_frames(pipeline, 'output.mp4')
