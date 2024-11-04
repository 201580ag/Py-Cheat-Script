import cv2
import numpy as np
from mss import mss
import time
from win32 import win32api
import win32con

# 화면 캡쳐 객체 생성
sct = mss()

# 모니터 해상도 및 상자 크기 설정
monX = 1920
monY = 1080
boxsize = 75

# HSV 색상 범위 설정
lower = np.array([139,96,129])
upper = np.array([169,255,255])

def grab():
    # 화면 캡쳐 함수
    mon2 = sct.monitors[2]
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
    # 마우스 이동 함수
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)

def process():
    # 화면 처리 함수
    hsv = cv2.cvtColor(input, cv2.COLOR_BGR2HSV)
    red_mask = cv2.inRange(hsv, lower, upper)
    res_red = cv2.bitwise_and(red_mask, red_mask, mask=red_mask)
    
    # 빨간색 객체 윤곽선 검출
    contours, hierarchy = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # print(len(contours))

    if len(contours) != 0:
        # 최대 면적의 윤곽선 선택
        maximum = max(contours, key=cv2.contourArea)
        moment = cv2.moments(res_red)
        if moment["m00"] == 0:
            return
        
        # 중심점 계산
        mid = boxsize / 2
        cX = int(moment["m10"] / moment["m00"])
        cY = int(moment["m01"] / moment["m00"])
        
        # 중심점 표시
        cv2.circle(input, (cX, cY), 5, (255, 255, 255), -1)
        
        # 마우스 이동 벡터 계산
        xf = -(mid - cX)
        yf = -(mid - cY)

        # 마우스 동작 확인 후 이동
        if is_activated():
            mouse_move(int(xf), int(yf))
    
    return 

def is_activated():
    # 마우스 클릭 여부 확인 함수
    return win32api.GetAsyncKeyState(0x01) != 0 or win32api.GetAsyncKeyState(0x02) != 0

while True:
    loop_time = time.time()
    input = grab()
    process()
    
    # 백그라운드에 사각형 그리기
    cv2.rectangle(input, (200, 375), (900, 900), (255, 239, 213), -1)
    
    # 화면 출력
    # cv2.imshow('input', input)
    
    # 프레임 간 간격 측정
    loop_time = time.time()

    # 종료 조건
    if (cv2.waitKey(1) & 0xFF) == ord("q"):
        cv2.destroyAllWindows()
        break
