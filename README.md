A fork of gambatte-terminal, using the iterm2 graphics protocol instead of blocks for pixel perfect graphics. Only supported on some terminals, (I use konsole).

The iterm2 protocol essentially just sends an encoded image to the terminal, which decodes the image and displays it. I chose the fpng library to encode the frames from gambatte very quickly with decent compression, and wrote a minimal for python wrapper (pybind11) for the only function I actually need.

I haven't tested over ssh yet.