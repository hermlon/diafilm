# diafilm

Diafilm is a small GUI utility to capture pictures from webcam based slide film scanners such as the SilverCrest Negative Digitiser SND 3600.

## Features

- automatically detect movement to the next slide and capture the image after some waiting time
- adjust webcam properties such as ...
- rotate pictures on the fly

## Libraries used

Diafilm is a Qt Application written in Python using PySide6. Further dependencies are OpenCV2 and superqt.

## How the "next slide" detection works

The image is converted to grayscale. Then a threshold is applied: everything below the threshold is converted to black, while everything above it is white. The if the percentage of black pixels is within the configured "black percentage" range (e.g. between 20 % and 80 %) the frame is regarded as a "black" frame. Every frame from the camera is being analyzed. After a configurable number of black frames (usually more than 2) and a following number of non-black frames (maybe 5, should be set according to how long the webcam takes to adjust brightness for a new slide) a new image is "taken". It then can be rotated and will be stored to disk when moving to the next slide (or closing the application).
