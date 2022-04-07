import numpy as np
import cv2


cap = cv2.VideoCapture(0)
# img = cv2.imread('data/nail.png')

while(True):

    ret, frame = cap.read()

    # convert img to greyscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # do Threshold
    ret, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    # cv2.imshow('threshold', thresh)

    # Find Edges
    edges = cv2.Canny(thresh, 20, 50)
    # cv2.imshow('1 - Canny Edges', edges)

    # Find some lines
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=15)

    # Draw lines on the image
    if lines is not None:
        print(lines.size)
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
    else:
        print("could not find any lines")

    # Show result
    cv2.imshow("Result Image", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# cv2.waitKey(0)
cap.release()
cv2.destroyAllWindows()
