import numpy as np
import cv2

cap = cv2.VideoCapture(0)
print('is cap opened: ', cap.isOpened())

ret, frame = cap.read()
print(ret)

# cap = cv2.imread('./nail.png')
# frame_HSV = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
# cv2.imshow('nail', frame_HSV)
# cv2.waitKey(0)

while(True):
    # Capture frame-by-frame
    if ret is True:
        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Display the resulting frame
        cv2.imshow('frame', gray)

    ret, frame = cap.read()
    print(ret)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()