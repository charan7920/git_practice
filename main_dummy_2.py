try:
    import os
    import math
    import traceback
    import time
    import numpy as np
    import cv2
    import sys
    import torch
    from os.path import dirname, abspath, join
except ImportError as ie:
    print(ie)

import visualization
from collections import namedtuple

#import pdb;pdb.set_trace()

is_save = None
if (len(sys.argv) == 1 or sys.argv[1] == "save"):
    is_save = True
elif (len(sys.argv) == 2 and sys.argv[1] == "show"):
    is_save = False

# project dir
project_dir = abspath(dirname(__name__))
media_dir = join(project_dir, 'media')
input_file = join(media_dir, '09.mp4')

display = None  # message
window_name = "tracking window"

tracking_id = 0
cp_prev_frame = []
# ---
tracking_object = {}
temp_dict = {}
first_run = True
Greet_timer = namedtuple(
    'Timer', ['wel_start', 'wel_status', 'by_start', 'by_status'])
Greet_timer.wel_status, Greet_timer.by_status = [False] * 2

# Custom yolo model
model = torch.hub.load('ultralytics/yolov5', 'custom',
                       path='./weights/best.pt')

# model params
model.conf = 0.50  # NMS confidence threshold
model.iou = 0.40  # NMS IoU threshold
# -------

try:
    capt = cv2.VideoCapture(input_file)

    width = int(capt.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capt.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(width, height)

    red_start = round((width / 100) * 20)
    red_end = round((width / 100) * 50)
    green_start = round((width / 100) * 50)
    green_end = round((width / 100) * 80)

    empty_arr = np.zeros(
        shape=(height, red_end - red_start, 3), dtype=np.uint8)
    red_arr = empty_arr.copy()
    green_arr = empty_arr.copy()

    red_arr[:, :, 2] = 255
    green_arr[:, :, 1] = 255

    font = cv2.FONT_HERSHEY_SIMPLEX

    # saving video
    writer = cv2.VideoWriter(filename='tracked video3.mp4',
                             fourcc=cv2.VideoWriter_fourcc(*'mp4v'),
                             fps=25,
                             frameSize=(width, height))

# full screen
    if is_save:
        print("save")
        # pass
    else:
        print("only show")
        cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


    class_obj = visualization.Visual(is_save = is_save, capt = capt, red_start = red_start,
                                           green_end = green_end,height = height, font = font,
                                           red_end = red_end, red_arr = red_arr, green_start = green_start,
                                           green_arr = green_arr, writer = writer, window_name = window_name,
                                           tracking_id = tracking_id, model = model, first_run = first_run,
                                           cp_prev_frame = cp_prev_frame, tracking_object = tracking_object,
                                           Greet_timer = Greet_timer, temp_dict = temp_dict)

    class_obj.processing_1()
    print("-----------------visualisation process 1 over")

except (Exception, KeyboardInterrupt) as ex:
    print(repr(ex))
    tb = traceback.extract_tb(ex.__traceback__)
    for t in tb:
        t = list(t)
        if not any([substr in str(t[0]) for substr in ['_libs', 'site-packages']]):
            print(f"Error details: file {t[0]} at line {t[1]} in {t[2]}")

finally:
    capt.release()
    writer.release()
    cv2.destroyAllWindows()
    print("whole code ended")
