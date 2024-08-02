import pyautogui
import time
import numpy as np
import cv2
import ctypes
from keys import *
from threading import Thread
from time import sleep
from queue import Queue
import math

# Ждем три секунды, успеваем переключиться на окно:
print('waiting for 3 seconds...')
time.sleep(3)

#ВНИМАНИЕ! PyAutoGUI НЕ ЧИТАЕТ В JPG!
title = './title.png'

nfs_window_location = None
searching_attempt = 1
while searching_attempt <= 5:
    nfs_window_location = pyautogui.locateOnScreen(title)

    if nfs_window_location is not None:
        print('nfs_window_location = ', nfs_window_location)
        break
    else:
        searching_attempt += 1
        time.sleep(1)
        print("attempt %d..." % searching_attempt)

if nfs_window_location is None:
    print('NFS Window not found')
    exit(1)

# Извлекаем из картинки-скриншота только данные окна NFS.
# Наша target-картинка - это заголовочная полоска окна.
# Для получения скриншота, мы берем ее левую точку (0),
# а к верхней (1) прибавляем высоту (3)
left = int(nfs_window_location[0])
top = int(nfs_window_location[1]+nfs_window_location[3])

# ВНИМАНИЕ!  У вас, скорее всего, будет другое разрешение, т.к. у меня 4К-монитор!
# Здесь надо выставить те параметры, которые вы задали в игре.
window_resolution = (640, 480)

window = (left, top, left+window_resolution[0], top+window_resolution[1])

cv2.namedWindow('result')


ranges = {
    'min_h1': {'current': 33, 'max': 180},
    'max_h1': {'current': 66, 'max': 180},
    'min_sv': {'current': 26, 'max': 255},
    'max_sv': {'current': 198, 'max': 255},
    'counters': {'current':0, 'max': 5}
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
POVOROTW = Queue(maxsize=1)
POVOROTA = Queue(maxsize=1)
POVOROTS = Queue(maxsize=1)
POVOROTD = Queue(maxsize=1)
POSITA = Queue(maxsize=5)


def Fpos():
    avg = 0
    for v in POSITA.queue:
        avg += v
    return avg / (POSITA.qsize() or 1)


def P_W():

    while (w := POVOROTW.get()) is not None:
        if w == 1:
            key_press(SC_W, interval=0.05)
        if w == 2:
            key_press(SC_W, interval=0.01)
        if w == 3:
            key_press(SC_W, interval=0.005)
alpha = 0.25
def P_A():
    cnt = 1
    while (a := POVOROTA.get()) is not None:
        if a == 1:
            key_press(SC_A, interval=alpha*.005)
        elif a == 2:
            key_press(SC_A, interval=alpha*.01)
        elif a == 3:
            key_press(SC_A, interval=alpha*.07)
        elif a == 4:
            key_press(SC_A, interval=alpha*.1)
        elif a == 5:
            key_press(SC_A, interval=alpha*.2)


def P_S():
    while (s := POVOROTS.get()) is not None:
        if s == 1:
            key_press(SC_S, interval=0.01)
        elif s == 2:
            key_press(SC_S, interval=0.1)

def P_D():
    cnt = 1
    while (d := POVOROTD.get()) is not None:
        if d == 1:
            key_press(SC_D, interval=alpha*.005)
        elif d == 2:
            key_press(SC_D, interval=alpha*.01)
        elif d == 3:
            key_press(SC_D, interval=alpha*.07)
        elif d == 4:
            key_press(SC_D, interval=alpha*.1)
        elif d == 5:
            key_press(SC_D, interval=alpha*.2)
        # print(f"d: {cnt}")
        # cnt += 1


W = Thread(target=P_W,)
A = Thread(target=P_A,)
S = Thread(target=P_S,)
D = Thread(target=P_D,)

W.start()
A.start()
S.start()
D.start()
while True:

    statusP = True

    pix = pyautogui.screenshot(region=(left, top, window_resolution[0], window_resolution[1]))
    numpix = cv2.cvtColor(np.array(pix), cv2.COLOR_RGB2BGR)

    frame = numpix[window_resolution[1]//2 + window_resolution[1]//10:, window_resolution[1] // 5:window_resolution[1] // -5, :]

    # frame = numpix[window_resolution[1] // 3:,: ,:]

    frame = cv2.GaussianBlur(frame, ksize=(9, 9), sigmaX=0, sigmaY=0)
    #filter_ = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    #frame = cv2.filter2D(frame, ddepth=0, kernel=filter_)
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    min_ = (ranges['min_h1']['current'], ranges['min_sv']['current'], ranges['min_sv']['current'])
    max_ = (ranges['max_h1']['current'], ranges['max_sv']['current'], ranges['max_sv']['current'])

    #41 70 31 255a

    min_1 = (30, ranges['min_sv']['current'], ranges['min_sv']['current'])
    max_1 = (40, ranges['min_sv']['current'], ranges['min_sv']['current'])

    min_2 = (0, ranges['min_sv']['current'], ranges['min_sv']['current'])
    max_2 = (10, ranges['min_sv']['current'], ranges['min_sv']['current'])

    min_3 = (170, ranges['min_sv']['current'], ranges['min_sv']['current'])
    max_3 = (180, ranges['min_sv']['current'], ranges['min_sv']['current'])

    maskG = cv2.inRange(frame_hsv, min_, max_)
    maskY = cv2.inRange(frame_hsv, min_1, max_1)
    mask2 = cv2.inRange(frame_hsv, min_2, max_2)
    mask3 = cv2.inRange(frame_hsv, min_3, max_3)
    maskR = cv2.bitwise_or(mask2, mask3)
    maska = cv2.bitwise_or(maskG, maskY)
    maska = cv2.bitwise_or(maska, maskR)

    result = cv2.bitwise_and(frame_hsv, frame_hsv, mask=maska)
    contours = cv2.findContours(maska, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours = contours[0]

    if contours:

        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        if len(contours) <= ranges['counters']['current']:
            cnt = contours[-1]
        #elif len(contours) <= 400:
            #cnt = contours[1]
        else:
            cnt = contours[0]
        cv2.drawContours(result, contours, 0, (255, 0, 0), 1)

        (x, y, w, h) = cv2.boundingRect(cnt)

        cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 1)

        (x1, y1), radius = cv2.minEnclosingCircle(cnt)
        center = (int(x1), int(y1))
        radius = int(radius)
        X = result.shape[0]
        Y = result.shape[1]
        startP = (Y//2, X)

        cv2.circle(result, center, radius, (0, 255, 0), 1)
        cv2.line(result, startP, center, (0, 255, 0), 1)

        position = x1 - Y//2
        if POSITA.full():
            POSITA.get()
        POSITA.put(position)


        # ((Y // 2 - x1) // 1) = Катет Горизонтально
        CUDA = 0
        hor = (Y // 2 - x1) // 1
        norm = X - y1
        if hor <= -1 :
            hor = hor*-1
            CUDA = 1
        tg = np.degrees(np.arctan(hor / norm))
        print(tg)

        avg_pos = Fpos()

        # if avg_pos >= 180:
        #     if not POVOROTD.full():
        #         POVOROTD.put(5)
        #         POVOROTS.put(2)
        # elif avg_pos >= 150:
        #     if not POVOROTD.full():
        #         POVOROTD.put(4)
        #         POVOROTS.put(1)
        # elif avg_pos >= 130:
        #     if not POVOROTD.full():
        #         POVOROTD.put(3)
        # elif avg_pos >= 70:
        #     if not POVOROTD.full():
        #         POVOROTD.put(2)
        #         POVOROTW.put(3)
        # elif avg_pos >= 30:
        #     if not POVOROTD.full():
        #         POVOROTD.put(1)
        #         POVOROTW.put(2)
        # elif avg_pos <= -180:
        #     if not POVOROTA.full():
        #         POVOROTA.put(5)
        #         POVOROTS.put(1)
        # elif avg_pos <= -150:
        #     if not POVOROTA.full():
        #         POVOROTA.put(4)
        #         POVOROTS.put(2)
        # elif avg_pos <= -130:
        #     if not POVOROTA.full():
        #         POVOROTA.put(3)
        # elif avg_pos <= -70:
        #     if not POVOROTA.full():
        #         POVOROTA.put(2)
        #         POVOROTW.put(3)
        # elif avg_pos <= -30:
        #     if not POVOROTA.full():
        #         POVOROTA.put(1)
        #         POVOROTW.put(2)
        # else:
        #     POVOROTW.put(1)

        if CUDA == 1:
            #Направо
            if tg <= 45:
                POVOROTD.put(5)
                POVOROTS.put(2)
            elif tg <= 35:
                POVOROTD.put(4)
                POVOROTS.put(1)
            elif tg <= 25:
                POVOROTD.put(3)
            elif tg <= 15:
                POVOROTD.put(2)
                POVOROTW.put(2)
            elif tg <= 5:
                POVOROTD.put(1)
                POVOROTW.put(3)
            else:
                POVOROTW.put(1)
        else:
            #Налево
            if tg <= 45:
                POVOROTA.put(5)
                POVOROTS.put(2)
            elif tg <= 35:
                POVOROTA.put(4)
                POVOROTS.put(1)
            elif tg <= 25:
                POVOROTA.put(3)
            elif tg <= 15:
                POVOROTA.put(2)
                POVOROTW.put(2)
            elif tg <= 5:
                POVOROTA.put(1)
                POVOROTW.put(3)
            else:
                POVOROTW.put(1)

    cv2.imshow('result', result)

    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()

POVOROTD.put(None)
POVOROTW.put(None)
POVOROTA.put(None)
POVOROTS.put(None)

W.join()
A.join()
S.join()
D.join()
