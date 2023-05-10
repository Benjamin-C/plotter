import numpy as np
import cv2

def findCenter(img, thresh=127):
    (thresh, bwi) = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY)

    rows = np.arange(0, np.shape(bwi)[0])
    cols = np.arange(0, np.shape(bwi)[1])
    x,y = np.meshgrid(cols, rows)

    wbi = (255 - bwi)
    totalWeight = np.sum(wbi)
    xweights = wbi * x
    yweights = wbi * y

    if totalWeight > 0:
        cX = int(np.round(np.sum(xweights)/totalWeight))
        cY = int(np.round(np.sum(yweights)/totalWeight))
        return cX, cY, wbi
    else:
        return (0, 0, wbi)