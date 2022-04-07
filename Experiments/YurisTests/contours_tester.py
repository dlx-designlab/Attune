import numpy as np
import cv2


image = cv2.imread('data/contours_test.png')


cv2.imshow('0 - Original Image', image)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# Find Canny edges
edged = cv2.Canny(gray, 150, 250)
cv2.imshow('1 - Canny Edges', edged)

# Find contours and print how many were found
# contours, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
# cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE

contours, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print "Number of contours found = ", len(contours)

for cont in contours:
    print 'Area: ', cv2.contourArea(cont)

# Draw all contours over blank image
cv2.drawContours(image, contours, -1, (0,255,0), 3)
cv2.imshow('3 - All Contours', image)
cv2.waitKey(0)

cv2.destroyAllWindows()