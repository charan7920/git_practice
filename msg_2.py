import cv2
from collections import namedtuple
import time


class wishing:
    def __init__(self,Greet_timer,frame,green_end, height ,font):
        self.Greet_timer = Greet_timer
        self.frame = frame
        self.green_end = green_end
        self.height = height
        self.font = font

    def processing_2(self):
        # Displays a message
        if self.Greet_timer.wel_status:
            cv2.putText(self.frame, text='Welcome!', org=(self.green_end + 20, self.height - 50), fontFace=self.font, fontScale=1.5, color=(0, 0, 0),
                        thickness=2, lineType=cv2.LINE_AA)
            if (time.time() - self.Greet_timer.wel_start) >= 2:
                self.Greet_timer.wel_status = False
                self.Greet_timer.wel_start = 0

        if self.Greet_timer.by_status:
            cv2.putText(self.frame, text='Bye!', org=(10, self.height - 50), fontFace=self.font, fontScale=2, color=(0, 0, 0),
                        thickness=2, lineType=cv2.LINE_AA)
            if (time.time() - self.Greet_timer.by_start) >= 2:
                self.Greet_timer.by_status = False
                self.Greet_timer.by_start = 0



