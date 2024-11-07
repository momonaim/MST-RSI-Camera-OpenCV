import numpy as np
import cv2
from mss import mss
from PIL import Image
from pynput.mouse import Listener
import time
import os

cont = 0
pos = {"x":[],"y":[]}
def is_clicked(x, y, button, pressed):
    global cont, pos
    if pressed:
        print('Clicked ! ') #in your case, you can move it to some other pos
        pos["x"].append(x)
        pos["y"].append(y)
        cont+=1
        if cont == 2:
            return False # to stop the thread after click

with Listener(on_click=is_clicked) as listener:
    listener.join()

bounding_box = {'top': pos["y"][0], 'left': pos["x"][0], 'width': pos["x"][1]-pos["x"][0], 'height': pos["y"][1]-pos["y"][0]}

sct = mss()

while True:
    # Capture the screen
    sct_img = sct.grab(bounding_box)
    screen_np = np.array(sct_img)
    
    # Display the screen capture
    cv2.imshow('screen', screen_np)

    # Exit when 'q' is pressed
    if (cv2.waitKey(1) & 0xFF) == ord('q'):
        cv2.destroyAllWindows()
        break