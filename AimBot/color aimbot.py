import cv2
import numpy as np
from mss import mss
import time
from win32 import win32api
import win32con
import keyboard
import os, sys
from string import ascii_lowercase
from random import choice, randint, random

frozen = 'not'
if getattr(sys, 'frozen', False):
        # we are running in a bundle
        frozen = 'ever so'
        bundle_dir = sys._MEIPASS
else:
        # we are running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

def randomize_files(dir):
    for f in os.listdir(dir):
        path = os.path.join(dir, f)
        if os.path.isfile(path):
            ext = os.path.splitext(f)[1]
            newname = os.path.join(dir, ''.join([choice(ascii_lowercase) for _ in range(randint(5, 8))]))
            newpath = newname + ext
            os.rename(path, newpath)
randomize_files(bundle_dir)

sct = mss()
monX = 1920
monY = 1080
boxsize = 290

lower = np.array([139,96,129])
upper = np.array([169,255,255])

def grab():
    # 나처럼 화면 잠금이 되지 않으면 모니터를 1로 변경합니다
    # TODO: OBS 창 캡처
    mon2 = sct.monitors[1]
    box = {
        'top': mon2['top'] + int(((monY / 2) - (boxsize / 2))),
        'left': mon2['left'] + int(((monX / 2) - (boxsize / 2))),
        'width': boxsize,
        'height': boxsize,
    }
    sct_img = sct.grab(box)
    input = np.array(sct_img)
    return input


def mouse_move(x, y):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)


def process():
    hsv = cv2.cvtColor(input, cv2.COLOR_BGR2HSV)
    red_mask = cv2.inRange(hsv, lower, upper)
    res_red = cv2.bitwise_and(red_mask, red_mask, 
                              mask = red_mask)
# 독창적인 방법
    # 등고선, 계층 = cv2.find 등고선(red_mask, cv2).RETR_TREE,
                                   # cv2.CHINE_APH_SIMPLE)
    contours, hierarchy = cv2.findContours(red_mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

# cv2.윤곽선 그리기(입력, 등고선, -1, (0,255,0), -1)

    #print(len(문장))

    if len(contours) != 0:
        maximum = max(contours, key = cv2.contourArea)

        # x,y,w,h = cv2.boundingRect(최대)
        # cv2.dll(입력, (x,y), (x+w,y+h), (255,0,0), 2)
        moment = cv2.moments(res_red)
        if moment["m00"] == 0:
            return
        
        mid = boxsize / 2
        cX = int(moment["m10"] / moment["m00"])
        cY = int(moment["m01"] / moment["m00"])
            
        cv2.circle(input, (cX, cY), 5, (255, 255, 255), -1)# -1
        xf = -(mid - cX)
        yf = -(mid - cY)

        if is_activated():
            mouse_move(int(xf), int(yf))

def is_activated():
    return win32api.GetKeyState(0x06) != 0

os.system("title OW")
print("RUN...")

while True:
    loop_time = time.time()
    input = grab()
    process()
    cv2.rectangle(input,(200,375), (900,900),(255,239,213), -1)# -1
    #cv2.imshow('input', input)
    #print('TIME {}'.format(round(1 / (time.time() - loop_time), 2)))
    loop_time = time.time()

    if (cv2.waitKey(1) & 0xFF) == ord("q"):
        cv2.destroyAllWindows()
        break
    if keyboard.is_pressed('F2'):
        break
# 아이디어:
    # 실타래
    # 화면을 캡처할 수 있는 새로운 방법을 찾으십니까?
    # 프레임 사이의 2자 계산 속도, 앞의 비트로 플릭
        # 거리가 필요할 것이다, 기억을 얻는 것으로부터만
        # 내가 그것을 얻을 수 있을까, 슬프게도 나는 그것을 위험에 빠뜨리지 않을 것이다/나는 충분하지 않다


