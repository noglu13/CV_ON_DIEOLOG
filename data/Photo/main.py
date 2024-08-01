# Ничего не делает, а должно зеркалить изображение.
import cv2
import os
img = cv2.imread("road-signs/approaching-a-pedestrian-crossing.jpg")
if img is None:
    print("ФАЙЛ НЕ НАЙДЕН")
    os._exit(1)
x_max, y_max, _ = img.shape
x = x_max
y = y_max

x = x//2
y = y//2
img[x, y]
print(x,y)
cv2.imshow('img',img)

