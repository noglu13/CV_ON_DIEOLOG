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
POSITA = Queue(maxsize=2)


def Fpos():
    avg = 0
    for v in POSITA.queue:
        avg += v
    return avg / (POSITA.qsize() or 1)


def P_W():

    while (w := POVOROTW.get()) is not None:
        key_press(SC_W, interval=w)


def P_A():
    while (a := POVOROTA.get()) is not None:
        key_press(SC_A, interval=a)


def P_S():
    while (s := POVOROTS.get()) is not None:
        key_press(SC_S, interval=s)


def P_D():
    while (d := POVOROTD.get()) is not None:
        key_press(SC_D, interval=d)


def PID():
    # Пропорцианально
    P1 = POSITA.get()
    P2 = POSITA.get()
    kf = P2 + P1
    #Интегрально
    Ki = -0.05 #Значениет регулируемое
    I = (P1*Ki) + (P2*Ki)
    #Диференциальное
    print()


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




        # ((Y // 2 - x1) // 1) = Катет Горизонтально
        CUDA = 0
        hor = (Y // 2 - x1) // 1
        norm = X - y1
        if hor <= -1 :
            hor = hor*-1
            CUDA = 1
        tg = np.degrees(np.arctan(hor / norm))
        up = X//2 - y1

        if POSITA.full():
            POSITA.get()
        POSITA.put(tg)
        tg = Fpos()
        print(tg)


        # if CUDA == 1:
        #     if up >= 0:
        #         #Направо
        #         if tg >= 55:
        #             POVOROTD.put(0.04)
        #             print("6D")
        #         elif tg >= 45:
        #             POVOROTD.put(0.02)
        #             POVOROTW.put(0.01)
        #             print("5D")
        #         elif tg >= 35:
        #             POVOROTD.put(0.03)
        #             POVOROTW.put(0.02)
        #             print("4D")
        #         elif tg >= 25:
        #             POVOROTD.put(0.03)
        #             POVOROTW.put(0.04)
        #             print("3D")
        #         elif tg >= 15:
        #             POVOROTD.put(0.02)
        #             POVOROTW.put(0.08)
        #             print("2D")
        #         elif tg >= 5:
        #             POVOROTD.put(0.01)
        #             POVOROTW.put(0.16)
        #             print("1D")
        #         else:
        #             POVOROTW.put(0.2)
        #     if hor >= 150 and up <= -10 and tg >= 60:
        #         POVOROTD.put(0.1)
        #         print("7D")
        #
        # else:
        #     if up >= 0:
        #         #Налево
        #         if tg >= 55:
        #             POVOROTA.put(0.04)
        #             print("6A")
        #         elif tg >= 45:
        #             POVOROTA.put(0.035)
        #             POVOROTW.put(0.01)
        #             print("5A")
        #         elif tg >= 35:
        #             POVOROTA.put(0.03)
        #             POVOROTW.put(0.02)
        #             print("4A")
        #         elif tg >= 25:
        #             POVOROTA.put(0.03)
        #             POVOROTW.put(0.04)
        #             print("3A")
        #         elif tg > 15:
        #             POVOROTA.put(0.02)
        #             POVOROTW.put(0.08)
        #             print("2A")
        #         elif tg >= 5:
        #             POVOROTA.put(0.01)
        #             POVOROTW.put(0.16)
        #             print("1A")
        #         else:
        #             POVOROTW.put(0.2)
        #     if hor >= 150 and up <= -10 and tg >= 60:
        #         POVOROTA.put(0.1)
        #         print("7A")



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

A.join()
S.join()
D.join()
