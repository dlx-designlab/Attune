# Capillaries recognition tests

import numpy as np
import cv2 as cv


im = cv.imread('data/caps_cropped.png')
imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
ret, thresh = cv.threshold(imgray, 100, 255, cv.THRESH_BINARY_INV)
contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

contours = sorted(contours, key=cv.contourArea, reverse=True)

print "Contours Count:", len(contours)

contImg = im
hullImg = imgray
for i in range(0, 3):
    cMoments = cv.moments(contours[i])
    cPos = (int(cMoments['m10']/cMoments['m00']), int(cMoments['m01']/cMoments['m00']))

    contImg = cv.drawContours(contImg, contours, i, (0, 255, 0), 2)
    contImg = cv.putText(contImg, str(i), cPos, cv.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

    epsilon = 0.01 * cv.arcLength(contours[i], True)
    approx = cv.approxPolyDP(contours[i], epsilon, True)
    hullImg = cv.drawContours(hullImg, [approx], -1, (255, 255, 255), 2)



cv.imshow("grey", imgray)
cv.imshow("thresh", thresh)
cv.imshow("contours", contImg)
cv.imshow("hulls", hullImg)
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