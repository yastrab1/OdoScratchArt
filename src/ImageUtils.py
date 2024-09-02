import cv2
import numpy as np
from PIL import Image


def pasteImageRGBA(background, foreground, position=(0,0)):

    # Ensure the background image has an alpha channel
    if background.shape[2] == 3:
        background = cv2.cvtColor(background, cv2.COLOR_BGR2BGRA)

    # Get the dimensions of the foreground image
    fg_h, fg_w, fg_channels = foreground.shape

    # Extract the alpha channel from the foreground image
    alpha_fg = foreground[:, :, 3] / 255.0

    # Extract the RGB channels of the foreground image
    rgb_fg = foreground[:, :, :3]

    # Position where the image will be placed
    x, y = position

    # Get the region of interest from the background image
    roi = background[y:y+fg_h, x:x+fg_w]

    # Extract the RGB channels of the region of interest from the background image
    rgb_bg = roi[:, :, :3]

    # Extract the alpha channel from the background image (if it exists)
    if roi.shape[2] == 4:
        alpha_bg = roi[:, :, 3] / 255.0
    else:
        alpha_bg = np.ones((fg_h, fg_w))

    # Blend the RGB channels using the alpha mask
    for c in range(0, 3):
        roi[:, :, c] = (alpha_fg * rgb_fg[:, :, c] + (1 - alpha_fg) * rgb_bg[:, :, c])

    # Blend the alpha channel
    roi[:, :, 3] = (alpha_fg * 255 + (1 - alpha_fg) * alpha_bg * 255)

    # Place the blended region back into the original background image
    background[y:y+fg_h, x:x+fg_w] = roi

    return background


def pasteMaskOnMask(back, front, x, y):
    fh, fw = front.shape

    alpha_foreground = front[:, :,]
    alpha_background = 1.0 - alpha_foreground

    back[y:y + fh, x:x + fw] = front*alpha_foreground + alpha_background*back[y:y + fh, x:x + fw]
    return back


def cv2ToPil(cv2_image):
    img = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    im_pil = Image.fromarray(img)
    return im_pil


def pilToCv2(im_pil):
    im_np = np.asarray(im_pil)
    im_np = cv2.cvtColor(im_np, cv2.COLOR_RGB2BGR)
    return im_np
