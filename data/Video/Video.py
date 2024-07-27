import cv2
import numpy as np

cap = cv2.VideoCapture(0)

cv2.namedWindow('result')

ranges = {
    'min_h1': {'current': 20, 'max': 180},
    'max_h1': {'current': 40, 'max': 180},
}


def trackbar_handler(name):
    def handler(x):
        global ranges
        ranges[name]['current'] = x

    return handler


for name in ranges:
    cv2.createTrackbar(name,
                       'result',
                       ranges[name]['current'],
                       ranges[name]['max'],
                       trackbar_handler(name)
                       )



while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame,1)
    frame = cv2.GaussianBlur(frame, ksize=(25, 25), sigmaX =0, sigmaY=0)


    filter_ = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    frame = cv2.filter2D(frame, ddepth=-1, kernel=filter_)


    frame_copy = frame.copy()

    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    min_ = (ranges['min_h1']['current'], 0, 0)
    max_ = (ranges['max_h1']['current'], 255, 255)

    mask = cv2.inRange(frame_hsv, min_, max_)
    result = cv2.bitwise_and(frame, frame, mask=mask)

    contours = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours = contours[0]
    if contours:
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        cv2.drawContours(result, contours, 0, (255, 0, 0), 1)
        cv2.drawContours(result, contours, 1, (255, 0, 0), 1)
        cv2.drawContours(result, contours, 2, (255, 0, 0), 1)

        (x, y, w, h) = cv2.boundingRect(contours[0])
        cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 1)
        (x1, y1), radius = cv2.minEnclosingCircle(contours[0])
        center = (int(x1), int(y1))
        radius = int(radius)
        cv2.circle(result, center, radius, (0, 255, 0), 1)

    cv2.imshow('mask', mask)
    cv2.imshow('result', result)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()