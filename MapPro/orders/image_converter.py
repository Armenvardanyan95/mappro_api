from PIL import Image
import numpy as np
import base64
from io import BytesIO

import os.path

script_dir = os.path.dirname(os.path.abspath(__file__))


def hex_to_rgb(value):
    """Return (red, green, blue) for the color given as #rrggbb."""
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def create_marker(hex_val):
    im = Image.open(os.path.join(script_dir, 'plain-marker.png'))

    data = np.array(im)  # "data" is a height x width x 4 numpy array
    red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability

    # Replace white with red... (leaves alpha values alone...)
    white_areas = (red == 255) & (blue == 255) & (green == 255)
    data[..., :-1][white_areas.T] = hex_to_rgb(hex_val)  # Transpose back needed

    im2 = Image.fromarray(data)
    size = 35, 35
    im2.thumbnail(size, Image.ANTIALIAS)
    im2.save(os.path.join(script_dir, 'new marker.png'))
    buffer = BytesIO()
    im2.save(buffer, format="PNG")
    img_str = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str




