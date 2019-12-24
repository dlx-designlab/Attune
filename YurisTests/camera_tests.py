import numpy as np
import cv2

cap = cv2.VideoCapture(0)

print('is cap opened: ', cap.isOpened())

# print(cap.get(cv2.CAP_PROP_AUTO_WB))
# print(cap.get(cv2.CAP_PROP_WB_TEMPERATURE))
# print(cap.get(cv2.CAP_PROP_FOCUS))
# print(cap.get(cv2.CAP_PROP_WB_TEMPERATURE))

# cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
# cap.set(cv2.CAP_PROP_FOCUS, 100)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# cap = cv2.imread('./nail.png')
# frame_HSV = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
# cv2.imshow('nail', frame_HSV)
# cv2.waitKey(0)

while(True):

    # Capture frame-by-frame
    ret, frame = cap.read()

    if ret is True:
        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Check Blur Amount
        fm = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Add Blur Value to the frame
        cv2.putText(frame, "Sharpness Index: {:.2f}".format(fm), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)

        # Display the resulting frame
        cv2.imshow('frame', frame)

    # print(ret)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()