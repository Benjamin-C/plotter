import numpy as np
import cv2

def findCenter(img, blur=51, thresh=127):
    grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    grayImage = cv2.medianBlur(grayImage, 1+((blur//2)*2))
    (thresh, bwi) = cv2.threshold(grayImage, thresh, 255, cv2.THRESH_BINARY)

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
        return (-1, -1, wbi)