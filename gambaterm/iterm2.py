import base64
from io import BytesIO
import numpy as np
import numpy.typing as npt
from .fpng import *

SCALE = 2

def set_scale(scale: float) -> None:
    global SCALE
    SCALE = scale

def make_image(image: npt.NDArray[np.uint32]) -> bytes:
    OSC = b'\033]'
    CSI = b'\033['
    ST  = b'\a'
    b = BytesIO()
    data = encode_image_to_memory((image<<8).byteswap()+0xff000000, 4, 0)
    b = BytesIO()
    b.write(OSC)
    b.write(b'1337;File=inline=1;')
    b.write(f'width={int(SCALE*160)}px'.encode('ascii'))
    b.write(b':')
    b.write(base64.b64encode(data))
    b.write(ST)
    b.write(CSI)
    b.write(b'H')
    b.seek(0)
    return b.read()
