from dataclasses import is_dataclass
import cv2
import math
import time
from collections import namedtuple
import msg_2
import keyboard
import msg_2


class Visual:

    def __init__(self, is_save, capt, red_start, green_end,
                 height, font, red_end, red_arr, green_start,
                     green_arr, writer, window_name, tracking_id, model, first_run,
                     cp_prev_frame, tracking_object, Greet_timer, temp_dict):

        self.tracking_id = tracking_id
        self.is_save = is_save
        self.capt = capt
        self.red_start = red_start
        self.green_end = green_end
        self.height = height
        self.font = font
        self.red_end = red_end
        self.red_arr = red_arr
        self.green_start = green_start
        self.green_arr = green_arr
        self.writer = writer
        self.window_name = window_name
        self.model = model
        self.first_run = first_run
        self.cp_prev_frame = cp_prev_frame
        self.tracking_object = tracking_object
        self.Greet_timer = Greet_timer
        self.temp_dict = temp_dict

    def processing_1(self):

        while self.capt.isOpened():
            cp_cur_frame = []

            ret, frame = self.capt.read()

            # break out of while loop if video ends
            if not ret:
                break

            # region of interest
            roi = frame[:, self.red_start:self.green_end, :]

            # convert BGR color map to RGB color map
            roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

            _, w1, _ = roi.shape
            middle = w1 / 2

            results = self.model(roi)
            boxes = results.pred[0][:, :4]  # x1, y1, x2, y2

            for bbox in boxes:
                x1, y1, x2, y2 = bbox
                cx = int((x1+x2) / 2)
                cy = int((y1+y2) / 2)

                cp_cur_frame.append((cx, cy))

                #cv2.circle(roi, (cx,cy), 3, (0,0,255), -1)
                # bounding box
                cv2.rectangle(roi, (int(x1), int(y1)),
                              (int(x2), int(y2)), (0, 255, 0), 2)

            # Runs only at the begining of the frame
            if self.first_run:
                for cx1, cy1 in cp_cur_frame:
                    for cx2, cy2 in self.cp_prev_frame:
                        distance = math.hypot(cx2-cx1, cy2-cy1)

                        if distance < 25:
                            self.temp_dict['cord'] = (cx1, cy1)
                            if cx1 <= middle:
                                self.temp_dict['cur_zone'] = 'r'
                            else:
                                self.temp_dict['cur_zone'] = 'g'
                            self.tracking_object[self.tracking_id] = self.temp_dict.copy(
                            )
                            self.tracking_id += 1

                if len(self.tracking_object) != 0:
                    self.first_run = False

            else:
                tracking_object_copy = self.tracking_object.copy()
                cp_cur_frame_copy = cp_cur_frame.copy()

                for obj_id, pt2 in tracking_object_copy.items():
                    object_exists = False
                    for pt in cp_cur_frame_copy:
                        distance = math.hypot(
                            pt2['cord'][0] - pt[0], pt2['cord'][1] - pt[1])

                        # update object position
                        if distance < 25:
                            data_dict = self.tracking_object[obj_id]
                            data_dict['cord'] = pt

                            if pt[0] < middle and data_dict['cur_zone'] == 'g':
                                data_dict['cur_zone'] = 'r'
                                data_dict['prev_zone'] = 'g'

                                if not self.Greet_timer.by_status:
                                    display = 'Bye!'
                                    self.Greet_timer.by_status = True
                                    self.Greet_timer.by_start = time.time()

                            elif pt[0] > middle and data_dict['cur_zone'] == 'r':
                                data_dict['cur_zone'] = 'g'
                                data_dict['prev_zone'] = 'r'

                                if not self.Greet_timer.wel_status:
                                    display = 'Welcome!'
                                    self.Greet_timer.wel_status = True
                                    self.Greet_timer.wel_start = time.time()

                            object_exists = True

                            if pt in cp_cur_frame:
                                cp_cur_frame.remove(pt)
                            continue

                    # remove id
                    if not object_exists:
                        self.tracking_object.pop(obj_id)

                # creating new ids
                for pt in cp_cur_frame:
                    self.temp_dict['cord'] = pt
                    if pt[0] <= middle:
                        self.temp_dict['cur_zone'] = 'r'
                    else:
                        self.temp_dict['cur_zone'] = 'g'
                    self.tracking_object[self.tracking_id] = self.temp_dict.copy(
                    )
                    self.tracking_id += 1

            for obj_id, pt in self.tracking_object.items():
                cv2.circle(roi, pt['cord'], 3, (137, 0, 0), -1)
                #cv2.putText(roi, str(obj_id), (pt['cord'][0], pt['cord'][1] - 7), 0, 0.5, (0,0,255),1)

            frame[:, self.red_start:self.green_end, :] = cv2.cvtColor(
                roi, cv2.COLOR_RGB2BGR)

            # Display message
            class2_obj = msg_2.wishing(self.Greet_timer, frame,
                                        self.green_end, self.height,
                                       self.font)
            class2_obj.processing_2()

            # Red zone
            frame[:, self.red_start:self.red_end, :] = cv2.addWeighted(src1=frame[:, self.red_start:self.red_end, :],
                                                                       alpha=0.8, src2=self.red_arr, beta=0.2, gamma=0)

            # Green Zone
            frame[:, self.green_start:self.green_end, :] = cv2.addWeighted(src1=frame[:, self.green_start:self.green_end, :],
                                                                           alpha=0.8, src2=self.green_arr, beta=0.2, gamma=0)

            # center points list previous frame
            self.cp_prev_frame = cp_cur_frame.copy()

            if self.is_save:
                self.writer.write(frame)
            else:
                cv2.imshow(self.window_name, frame)

            # global variables
            self.temp_dict.clear()
            if self.tracking_id > 1000:
                self.tracking_id = 1

            if self.is_save and KeyboardInterrupt: # 0xFF == ord('q')
                print("break for save")
                break

            elif cv2.waitKey(1) & 0xFF == ord('q'):
                print("break key for show")
                break

            #print(self.is_save)

            # try:
            #     if self.is_save & 0xFF == ord('q'):
            #         break

            # except KeyboardInterrupt:
            #     if cv2.waitKey(1) & 0xFF == ord('q'):
            #         print("break key")
            #         break

    # print("done")

            # if self.is_save and keyboard.is_pressed("q"):
            #     print("break for save")
            #     break
            # elif cv2.waitKey(1) & 0xFF == ord('q'):
            #     print("break for show")
            #     break
