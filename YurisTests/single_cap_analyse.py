# Capillaries recognition tests
# Tested in in Python 2.7
# Open CV 4.0.0

import numpy as np
import cv2 as cv

print 'openCV version: ', cv.__version__

# im = cv.imread('data/caps_cropped.png')
im = cv.imread('data/single_cap.png')

# Smoothing
# smoothed1 = cv.medianBlur(im, 5)
# smoothed2 = cv.bilateralFilter(im, 5, 10, 100)
smoothed1 = cv.fastNlMeansDenoisingColored(im, None, 3, 3, 7, 21)
smoothed2 = cv.fastNlMeansDenoisingColored(im, None, 6, 6, 7, 21)
smoothed3 = cv.fastNlMeansDenoisingColored(im, None, 4, 15, 7, 21)

# Find Edges
edged = cv.Canny(smoothed3, 40, 60)

# Convert image to gray-scale
imgray = cv.cvtColor(smoothed3, cv.COLOR_BGR2GRAY)

# Apply Threshold
ret, thresh = cv.threshold(imgray, 90, 255, cv.THRESH_BINARY_INV)

# Show Results
cv.imshow('Original Color', im)
cv.imshow('Smoothed1', smoothed1)
cv.imshow('Smoothed2', smoothed2)
cv.imshow('Smoothed3', smoothed3)
cv.imshow('Smoothed Grey', imgray)
cv.imshow('Threshed', thresh)
cv.imshow('Canny Edges', edged)
cv.waitKey(0)
cv.destroyAllWindows()

# # Split to channels
# B, G, R = cv.split(im)
# cv.imshow("Red", R)
# cv.imshow("Green", G)
# cv.imshow("Blue", B)
# cv.waitKey(0)
# cv.destroyAllWindows()

# Find contours and sort by length
# For better accuracy, use binary images. So Before finding contours, apply threshold or canny edge detection.
contours, hierarchy = cv.findContours(thresh.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=cv.contourArea, reverse=True)
print "Contours Count:", len(contours)

contImg = im
hullImg = imgray
for i in range(0, len(contours)):

    # Get Contour length
    cLength = cv.arcLength(contours[i], True)

    # Process only long contours
    if cLength > 300:

        # Get Area and calculate average diameter
        cArea = cv.contourArea(contours[i])
        cDiameter = cArea/(cLength/2)

        # Get contour moments
        cMoments = cv.moments(contours[i])

        # Find contour center point
        cPos = (int(cMoments['m10']/cMoments['m00'])-50, int(cMoments['m01']/cMoments['m00']))

        # draw contours and caption
        contImg = cv.drawContours(contImg, contours, i, (0, 255, 0), 1)
        cInfo = 'L:{:.2f} D:{:.2f}'.format(cLength, cDiameter)
        contImg = cv.putText(contImg, cInfo, cPos, cv.FONT_HERSHEY_PLAIN, 0.8, (255, 255, 255), 1)

        # Draw Simplified Contours
        # epsilon = 0.01 * cv.arcLength(contours[i], True)
        # approx = cv.approxPolyDP(contours[i], epsilon, True)
    # hullImg = cv.drawContours(hullImg, [approx], -1, (255, 255, 255), 2)


# Display Images
cv.imshow("grey", imgray)
cv.imshow("thresh", thresh)
cv.imshow("contours", contImg)
# cv.imshow("hulls", hullImg)
cv.waitKey(0)
cv.destroyAllWindows()


# element = cv2.getStructuringElement(cv2.MORPH_ERODE, (3, 3))
# done = False
#
# while (not done):
#     eroded = cv2.erode(img, element)
#     temp = cv2.dilate(eroded, element)
#     temp = cv2.subtract(img, temp)
#     skel = cv2.bitwise_or(skel, temp)
#     img = eroded.copy()
#
#     zeros = size - cv2.countNonZero(img)
#     if zeros == size:
#         done = True
#
# cv2.imshow("skel", skel)
# cv2.waitKey(0)
# cv2.destroyAllWindows()