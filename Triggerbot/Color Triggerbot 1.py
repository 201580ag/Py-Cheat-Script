import keyboard
import time
import ctypes
import PIL.ImageGrab
import PIL.Image
import winsound 
import os
import mss
from colorama import Fore, Style, init
S_HEIGHT, S_WIDTH = (PIL.ImageGrab.grab().size)
PURPLE_R, PURPLE_G, PURPLE_B = (250, 100, 250)
TOLERANCE = 60
GRABZONE = 10
TRIGGER_KEY = "ctrl + alt"
SWITCH_KEY = "ctrl + tab"
GRABZONE_KEY_UP = "ctrl + up"
GRABZONE_KEY_DOWN = "ctrl + down"
mods = ["slow", "medium", "fast"]
 
class FoundEnemy(Exception):
    pass
 
class triggerBot():
    def __init__(self):
        self.toggled = False
        self.mode = 1
        self.last_reac = 0
 
    def toggle(self):
        self.toggled = not self.toggled
 
    def switch(self):
        if self.mode != 2:
            self.mode += 1
        else:
            self.mode = 0
        if self.mode == 0:
            winsound.Beep(200, 200)
        if self.mode == 1:
            winsound.Beep(200, 200)
            winsound.Beep(200, 200)
        if self.mode == 2:
            winsound.Beep(200, 200)
            winsound.Beep(200, 200)
            winsound.Beep(200, 200)
    def click(self):
        ctypes.windll.user32.mouse_event(2, 0, 0, 0,0) # left down
        ctypes.windll.user32.mouse_event(4, 0, 0, 0,0) # left up
        
    def approx(self, r, g ,b):
        return PURPLE_R - TOLERANCE < r < PURPLE_R + TOLERANCE and PURPLE_G - TOLERANCE < g < PURPLE_G + TOLERANCE and PURPLE_B - TOLERANCE < b < PURPLE_B + TOLERANCE
 
    def grab(self):
        with mss.mss() as sct:
            bbox=(int(S_HEIGHT/2-GRABZONE), int(S_WIDTH/2-GRABZONE), int(S_HEIGHT/2+GRABZONE), int(S_WIDTH/2+GRABZONE))
            sct_img = sct.grab(bbox)
            # Convert to PIL/Pillow Image
            return PIL.Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
    def scan(self):
        start_time = time.time()
        pmap = self.grab()
        try:
            for x in range(0, GRABZONE*2):
                for y in range(0, GRABZONE*2):
                    r, g, b = pmap.getpixel((x,y))
                    if self.approx(r, g, b):
                        raise FoundEnemy
        except FoundEnemy:
            self.last_reac = int((time.time() - start_time)*1000)
            self.click()
            if self.mode == 0:
                time.sleep(0.01)
            if self.mode == 1:
                time.sleep(0.25)
            if self.mode == 2:
                time.sleep(0.12)
            print_banner(self)
 
def print_banner(bot: triggerBot):
    os.system("cls")
    print(Style.BRIGHT + Fore.CYAN + """ __       __   ______    ______   _______    ______   __     __ 
|  \     /  \ /      \  /      \ |       \  /      \ |  \   |  \\
| $$\   /  $$|  $$$$$$\|  $$$$$$\| $$$$$$$\|  $$$$$$\| $$   | $$
| $$$\ /  $$$| $$__| $$| $$   \$$| $$__| $$| $$__| $$| $$   | $$
| $$$$\  $$$$| $$    $$| $$      | $$    $$| $$    $$ \$$\ /  $$
| $$\$$ $$ $$| $$$$$$$$| $$   __ | $$$$$$$\| $$$$$$$$  \$$\  $$ 
| $$ \$$$| $$| $$  | $$| $$__/  \| $$  | $$| $$  | $$   \$$ $$  
| $$  \$ | $$| $$  | $$ \$$    $$| $$  | $$| $$  | $$    \$$$   
 \$$      \$$ \$$   \$$  \$$$$$$  \$$   \$$ \$$   \$$     \$ 
                    MACRAV alpha Build v0.4""" + Style.RESET_ALL)
    print("====== Controls ======")
    print("Activate Trigger Bot :", Fore.YELLOW + TRIGGER_KEY + Style.RESET_ALL)
    print("Switch fire mode     :", Fore.YELLOW + SWITCH_KEY + Style.RESET_ALL)
    print("Change Grabzone      :", Fore.YELLOW + GRABZONE_KEY_UP + "/" + GRABZONE_KEY_DOWN + Style.RESET_ALL)
    print("==== Information =====")
    print("Mode                 :", Fore.CYAN + mods[bot.mode] + Style.RESET_ALL)
    print("Grabzone             :", Fore.CYAN + str(GRABZONE) + "x" + str(GRABZONE) + Style.RESET_ALL)
    print("Activated            :", (Fore.GREEN if bot.toggled else Fore.RED) + str(bot.toggled) + Style.RESET_ALL)
    print("Last reaction time   :", Fore.CYAN + str(bot.last_reac) + Style.RESET_ALL + " ms ("+str((bot.last_reac)/(GRABZONE*GRABZONE))+"ms/pix)")
 
if __name__ == "__main__":
    bot = triggerBot()
    print_banner(bot)
    while True:
        if keyboard.is_pressed(SWITCH_KEY):
            bot.switch()
            print_banner(bot)
            while keyboard.is_pressed(SWITCH_KEY):
                pass
        if keyboard.is_pressed(GRABZONE_KEY_UP):
            GRABZONE += 5
            print_banner(bot)
            winsound.Beep(400, 200)
            while keyboard.is_pressed(GRABZONE_KEY_UP):
                pass
        if keyboard.is_pressed(GRABZONE_KEY_DOWN):
            GRABZONE -= 5
            print_banner(bot)
            winsound.Beep(300, 200)
            while keyboard.is_pressed(GRABZONE_KEY_DOWN):
                pass
        if keyboard.is_pressed(TRIGGER_KEY):
            bot.toggle()
            print_banner(bot)
            if bot.toggled:
                winsound.Beep(440, 75)
                winsound.Beep(700, 100)
            else:
                winsound.Beep(440, 75)
                winsound.Beep(200, 100)
            while keyboard.is_pressed(TRIGGER_KEY):
                pass
        if bot.toggled:
            bot.scan()