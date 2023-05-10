import cv2
import numpy as np

originalImage = cv2.imread('testimg/largedot-dirty.png')
img = originalImage
grayImage = cv2.cvtColor(originalImage, cv2.COLOR_BGR2GRAY)
grayImage = cv2.medianBlur(grayImage, 51)
  
def findCenter(img):
    (thresh, bwi) = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

    rows = np.arange(0, np.shape(bwi)[0])
    cols = np.arange(0, np.shape(bwi)[1])
    x,y = np.meshgrid(cols, rows)

    wbi = (255 - bwi)
    totalWeight = np.sum(wbi)
    xweights = wbi * x
    yweights = wbi * y

    cX = int(np.round(np.sum(xweights)/totalWeight))
    cY = int(np.round(np.sum(yweights)/totalWeight))

    return cX, cY, img

cX, cY = findCenter(grayImage)

cv2.circle(img, (cX, cY), 5, (255, 0, 255), -1)
cv2.putText(img, "centroid", (cX - 25, cY - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
cv2.imshow("Image", img)
cv2.waitKey(0)

exit()
# cv2.imshow('Original image',originalImage)
# cv2.imshow('Black white image', blackAndWhiteImage)
# edges = cv2.Canny(image=grayImage, threshold1=100, threshold2=200) # Canny Edge Detection

# cv2.imshow('Canny Edge Detection', edges)
# cv2.waitKey(0)

# minDist = 100
# param1 = 30 #500
# param2 = 50 #200 #smaller value-> more false circles
# minRadius = 100
# maxRadius = 500 #10

# # docstring of HoughCircles: HoughCircles(image, method, dp, minDist[, circles[, param1[, param2[, minRadius[, maxRadius]]]]]) -> circles
# circles = cv2.HoughCircles(grayImage, cv2.HOUGH_GRADIENT, 1, minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)

# # circles = cv2.HoughCircles(blackAndWhiteImage, cv2.HOUGH_GRADIENT, 1.2, minDist=50, minRadius=30, maxRadius=500)
# # ensure at least some circles were found
# if circles is not None:
# 	# convert the (x, y) coordinates and radius of the circles to integers
# 	circles = np.round(circles[0, :]).astype("int")
# 	# loop over the (x, y) coordinates and radius of the circles
# 	for (x, y, r) in circles:
# 		# draw the circle in the output image, then draw a rectangle
# 		# corresponding to the center of the circle
# 		cv2.circle(originalImage, (x, y), r, (0, 255, 0), 4)
# 		cv2.rectangle(originalImage, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
# 	# show the output image

# else:
# 	print("No circles found")
	

# convert image to grayscale image
gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
 
# convert the grayscale image to binary image
ret,thresh = cv2.threshold(gray_image,127,255,0)
 
# calculate moments of binary image
M = cv2.moments(thresh)
 
# calculate x,y coordinate of center
cX = int(M["m10"] / M["m00"])
cY = int(M["m01"] / M["m00"])
 
# put text and highlight the center
cv2.circle(img, (cX, cY), 5, (255, 0, 255), -1)
cv2.putText(img, "centroid", (cX - 25, cY - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
 
# display the image
cv2.imshow("Image", img)
cv2.imshow("Thresh", thresh)
cv2.waitKey(0)

cgrayImage = cv2.cvtColor(grayImage, cv2.COLOR_GRAY2BGR)

# cv2.imshow("output", np.hstack([originalImage, cgrayImage]))
# cv2.imshow("Result", originalImage)
cv2.waitKey(0)
cv2.destroyAllWindows()