import cv2
from math import pow, sqrt
from mss import mss
import numpy as np
from win32 import win32api
import win32con
import lib.viz as viz
import keyboard

if __debug__:
    cv2.namedWindow('BOT', cv2.WINDOW_NORMAL)

# 대상을 검색할 창의 크기(픽셀)
# 즉, SQUARE_SIZE 600 => 600 x 600px000
SQUARE_SIZE = 350 #350~450
viz.SQUARE_SIZE = SQUARE_SIZE

# 문자의 중심이 될 수 있는 최대 픽셀 거리
# 그들을 붙잡기 전일 수 있다.
TARGET_SIZE = 150 #기본100 보통150
MAX_TARGET_DISTANCE = sqrt(2 * pow(TARGET_SIZE, 2))
viz.TARGET_SIZE = TARGET_SIZE
viz.MAX_TARGET_DISTANCE = MAX_TARGET_DISTANCE

# 선택한 창 사각형을 캡처할 mss 인스턴스 생성
sct = mss()

# 첫 번째 모니터를 사용하여 원하는 모니터 번호로 변경
dimensions = sct.monitors[1]

# 구문 분석할 화면의 중심 제곱 계산
dimensions['left'] = int((dimensions['width'] / 2) - (SQUARE_SIZE / 2))
dimensions['top'] = int((dimensions['height'] / 2) - (SQUARE_SIZE / 2)) #/ 1.9
dimensions['width'] = SQUARE_SIZE
dimensions['height'] = SQUARE_SIZE

# Windows API를 호출하여 다음과 같은 마우스 이동 이벤트를 시뮬레이션합니다.
#  OW로 보낸
def mouse_move(x, y):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)

# Caps Lock 키를 눌렀는지 여부를 결정합니다.
def is_activated():
    #return win32api.GetAsyncKeyState(0x14) != 0 
    return win32api.GetKeyState(0x06) != 0

#당신이 설정하고 싶은 어떤 키로도 그것을 대체하세요.

def locate_target(target):
    # 윤곽의 중심을 계산하다
    moment = cv2.moments(target)
    if moment["m00"] == 0:
        return

    cx = int(moment["m10"] / moment["m00"])
    cy = int(moment["m01"] / moment["m00"])

    mid = SQUARE_SIZE / 2
    x = -(mid - cx) if cx < mid else cx - mid
    y = -(mid - cy) if cy < mid else cy - mid

    target_size = cv2.contourArea(target)
    distance = sqrt(pow(x, 2) + pow(y, 2))

    # 여기에 확실히 좋은 장소가 있다.
    # 목표물의 크기와 관련된 민감도를 위해.
    # 및 거리
    slope = ((1.0 / 3.0) - 1.0) / (MAX_TARGET_DISTANCE / target_size)
    multiplier = ((MAX_TARGET_DISTANCE - distance) / target_size) * slope + 1

    if is_activated():
        mouse_move(int(x * multiplier), int(y * multiplier))
    
    if __debug__:
        # 선택한 대상의 윤곽선을 녹색으로 그립니다.
        cv2.drawContours(frame, [target], -1, (0, 255, 0), 2)
        # 질량중심에 흰색의 작은 원을 그리다.
        cv2.circle(frame, (cx, cy), 10, (255, 255, 255), -1)# 7 255 255 255 -1

print("Running...", 'red')
print("")

# 주 라이프사이클
while True:
    frame = np.asarray(sct.grab(dimensions))
    contours = viz.process(frame)

# 지금은 가장 큰 윤곽선 일치를 확인해 보십시오.
    if len(contours) > 1:
        # contour[0] == 경계 창틀
        # contour[1] == 가장 가까운/가장 큰 인물
        locate_target(contours[1])

    if __debug__:
        # 녹색 윤곽선은 "캐릭터"와 일치합니다.
        cv2.drawContours(frame, contours, -1, (0, 10000, 0), 1)#0 255 0
        cv2.imshow('BOT', frame)

    # 프로그램을 중지하려면 'q'를 누르십시오.
    if cv2.waitKey(25) & 0xFF == ord("q"):
             break
    # 백그라운드 중지
    if keyboard.is_pressed('F2'):
        break

sct.close()
cv2.destroyAllWindows()