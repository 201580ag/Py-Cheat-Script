#include <windows.h>
#include <iostream>
#include <vector>
#include <cmath>

// 모니터 해상도 및 상자 크기
const int monX = 1920;
const int monY = 1080;
const int boxsize = 75;

// 마젠타 색상의 RGB 범위 정의
const int lowerR = 200, lowerG = 0, lowerB = 200;
const int upperR = 255, upperG = 100, upperB = 255;

// 화면 캡처 함수
HBITMAP CaptureScreen(int x, int y, int width, int height, HDC hdcScreen, HDC hdcMem) {
    HBITMAP hbmScreen = CreateCompatibleBitmap(hdcScreen, width, height);
    SelectObject(hdcMem, hbmScreen);
    BitBlt(hdcMem, 0, 0, width, height, hdcScreen, x, y, SRCCOPY);
    return hbmScreen;
}

// RGB 데이터를 추출하여 특정 색상 감지
POINT DetectColor(HBITMAP hBitmap, int width, int height) {
    BITMAP bmp;
    GetObject(hBitmap, sizeof(BITMAP), &bmp);

    POINT center = { 0, 0 };
    int count = 0;

    std::vector<BYTE> buffer(bmp.bmWidthBytes * bmp.bmHeight);
    GetBitmapBits(hBitmap, buffer.size(), buffer.data());

    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            int idx = y * bmp.bmWidthBytes + x * 4; // 4 bytes per pixel (BGRA)

            BYTE b = buffer[idx];
            BYTE g = buffer[idx + 1];
            BYTE r = buffer[idx + 2];

            if (r >= lowerR && r <= upperR && g >= lowerG && g <= upperG && b >= lowerB && b <= upperB) {
                center.x += x;
                center.y += y;
                ++count;
            }
        }
    }

    if (count > 0) {
        center.x /= count;
        center.y /= count;
    }

    return center;
}

// 마우스 이동 함수
void MoveMouse(int dx, int dy) {
    INPUT input = { 0 };
    input.type = INPUT_MOUSE;
    input.mi.dx = dx;
    input.mi.dy = dy;
    input.mi.dwFlags = MOUSEEVENTF_MOVE;
    SendInput(1, &input, sizeof(INPUT));
}

// 마우스 버튼 눌림 상태 확인 함수
bool IsMouseButtonPressed() {
    return (GetAsyncKeyState(VK_LBUTTON) & 0x8000) || (GetAsyncKeyState(VK_RBUTTON) & 0x8000);
}

// 메인 함수
int main() {
    HDC hdcScreen = GetDC(NULL);
    HDC hdcMem = CreateCompatibleDC(hdcScreen);

    RECT monitorRect = { 0, 0, monX, monY };
    int boxX = (monX / 2) - (boxsize / 2);
    int boxY = (monY / 2) - (boxsize / 2);

    while (true) {
        HBITMAP hBitmap = CaptureScreen(boxX, boxY, boxsize, boxsize, hdcScreen, hdcMem);

        POINT colorCenter = DetectColor(hBitmap, boxsize, boxsize);
        if (colorCenter.x > 0 || colorCenter.y > 0) {
            if (IsMouseButtonPressed()) { // 마우스 클릭 상태 확인
                int mid = boxsize / 2;
                int dx = colorCenter.x - mid;
                int dy = colorCenter.y - mid;

                MoveMouse(dx, dy);
            }
        }

        DeleteObject(hBitmap);
        Sleep(10); // CPU 사용량 조절
    }

    DeleteDC(hdcMem);
    ReleaseDC(NULL, hdcScreen);
    return 0;
}
