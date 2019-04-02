import numpy as np
import cv2 as cv


im = cv.imread('data/caps_cropped.png')
imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
ret, thresh = cv.threshold(imgray, 100, 255, cv.THRESH_BINARY_INV)
contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

contours = sorted(contours, key=cv.contourArea, reverse=True)

print "Contours Count:", len(contours)

cnt = contours[1]
print cnt


contImg = cv.drawContours(im, contours, 0, (0,255,0), 2)

cv.imshow("grey", imgray)
cv.imshow("thresh", thresh)
cv.imshow("contours", contImg)
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