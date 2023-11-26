import cv2
import numpy as np
import os
import time
import pytesseract
import sys
import win32gui, win32ui, win32con

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from windowcapture import grab_screen, list_window_names, find_target_window

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# windows scaling
SCALE_FACTOR = 1
WINDOW_WIDTH = int(2560 * SCALE_FACTOR)
WINDOW_HEIGHT = int(1440 * SCALE_FACTOR)

def auto_canny(image, sigma=0.33):
	# compute the median of the single channel pixel intensities
	v = np.median(image)
	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv2.Canny(image, lower, upper)
	# return the edged image
	return edged

def process_img(original_img):
    processed_img = original_img.copy()
    # processed_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
    # processed_img = auto_canny(processed_img)

    # filter with masking
    lower_range = np.array([200, 200, 200])  # Set the Lower range value of color in BGR
    upper_range = np.array([255, 255, 255])   # Set the Upper range value of color in BGR
    mask = cv2.inRange(processed_img, lower_range,upper_range) # Create a mask with range
    processed_img = cv2.bitwise_and(processed_img, processed_img, mask=mask)  # Performing bitwise and operation with mask in img variable

    return processed_img

def main():
    # call to list window names (debug)
    # list_window_names()

    # initialize the WindowCapture class (debug)
    # loop_time = time.time()

    try:
        argv1 = sys.argv[1]
    except IndexError:
        argv1 = "Minecraft*"

    target_window: str = find_target_window(argv1)
    hwnd = win32gui.FindWindow(None, target_window)
    win = win32ui.CreateWindowFromHandle(hwnd)
    print(target_window)
    print("press q to quit")

    # grab game window size
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    print(f"{x=}, {y=}, {w=}, {h=}")

    just_fished = False
    counter = 1 
    while True:
        # get an updated image of the game
        original_img = grab_screen((w-500, h-400, w-10, h-80), target_window) # minecraft audio subtitle

        # processing the image
        processed_img = original_img
        # processed_img = process_img(original_img)

        # show the image
        cv2.namedWindow("Resized_Window", cv2.WINDOW_NORMAL) # display window
        # resize window
        img_h, img_w = original_img.shape[:2]
        cv2.resizeWindow("Resized_Window", int(img_w * SCALE_FACTOR), int(img_h * SCALE_FACTOR))
        cv2.imshow("Resized_Window", processed_img) # show img on windows

        # debug the loop rate
        # print(f'FPS {1 / (time.time() - loop_time):.2f}')
        # loop_time = time.time()

        # press 'q' with the output window focused to exit.
        # waits 1 ms every loop to process key presses
        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            break

        # process
        # print(pytesseract.image_to_data(original_img))
        img2Str = pytesseract.image_to_string(original_img)
        # print(img2Str)
        if not just_fished and "obber splashes" in img2Str:
            print(f"Fishing Bobber splashes {counter}")
            counter += 1
            win.SendMessage(win32con.WM_RBUTTONDOWN, 0x0, 0)
            win.SendMessage(win32con.WM_RBUTTONUP, 0x0, 0) 
            time.sleep(1)
            win.SendMessage(win32con.WM_RBUTTONDOWN, 0x0, 0)
            win.SendMessage(win32con.WM_RBUTTONUP, 0x0, 0) 
            just_fished = True
        elif just_fished:
            time.sleep(3)
            just_fished = False

        time.sleep(0.4)

if __name__ == '__main__':
    main()
