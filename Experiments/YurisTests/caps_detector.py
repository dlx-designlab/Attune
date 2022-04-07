# Capillaries recognition tests

import numpy as np
import cv2 as cv


im = cv.imread('data/caps_cropped.png')
imGray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
imHLS = cv.cvtColor(im, cv.COLOR_BGR2HLS)


# Filter Capillaries
# capillaryColorUpper = cv.Vex

# # Split to channels
# B, G, R = cv.split(im)
# cv.imshow("Red", R)
# cv.imshow("Green", G)
# cv.imshow("Blue", B)
# cv.waitKey(0)
# cv.destroyAllWindows()




# Apply Threshold
ret, thresh = cv.threshold(imGray, 100, 255, cv.THRESH_BINARY_INV)

# Find contours
contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
# Sort contours by length
contours = sorted(contours, key=cv.contourArea, reverse=True)
print("Contours Count:", len(contours))

contImg = im
hullImg = imGray
for i in range(0, 3):

    # Get contour moments
    cMoments = cv.moments(contours[i])

    # Get Contour length
    cLength = ("Length: %.2f" % int(cv.arcLength(contours[i], False)))

    # Find contour center point
    cPos = (int(cMoments['m10']/cMoments['m00']), int(cMoments['m01']/cMoments['m00']))

    # draw contours and caption
    contImg = cv.drawContours(contImg, contours, i, (0, 255, 0), 1)
    contImg = cv.putText(contImg, str(cLength), cPos, cv.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

    # Draw Simplified Contours
    epsilon = 0.01 * cv.arcLength(contours[i], True)
    approx = cv.approxPolyDP(contours[i], epsilon, True)
    hullImg = cv.drawContours(hullImg, [approx], -1, (255, 255, 255), 2)


# Display Images
cv.imshow("grey", imGray)
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