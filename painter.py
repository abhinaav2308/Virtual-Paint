import cv2
import numpy as np
import time
import os 

import track_hands as TH

# Create temporary window
cv2.namedWindow("paint", cv2.WINDOW_NORMAL)

# Get screen resolution
screen_width, screen_height = 1080, 720  # Replace with actual screen resolution
_, _, actual_screen_width, actual_screen_height = cv2.getWindowImageRect("paint")

# Destroy temporary window
cv2.destroyWindow("paint")

# Set window size
window_width, window_height = max(screen_width, actual_screen_width), max(screen_height, actual_screen_height)
cv2.namedWindow("paint", cv2.WINDOW_NORMAL)
cv2.resizeWindow("paint", window_width, window_height)


brush_thickness = 10
eraser_thickness = 30
image_canvas = np.zeros((720, 1280, 3), np.uint8)


currentT = 0
previousT = 0

header_img = "Images"
header_img_list = os.listdir(header_img)
overlay_image = []


for i in header_img_list:
    image = cv2.imread(f'{header_img}/{i}')
    overlay_image.append(image)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

cap.set(cv2.CAP_PROP_FPS, 60)
default_overlay = overlay_image[0]
draw_color = (255, 51, 51)


detector = TH.handDetector(min_detection_confidence=.85)

xp = 0
yp = 0

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame[0:125, 0:640] = default_overlay
    cv2.putText(frame, 'Air Paint', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, draw_color, 5, cv2.LINE_AA)
    cv2.putText(frame, 'Size:', (5, 119), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.rectangle(frame, (50, 109), (150, 121), (0, 0, 0), -1)
    cv2.rectangle(frame, (152, 105), (252, 123), (0, 0, 0), -1)

    if brush_thickness == 10:
        cv2.rectangle(image_canvas, (50, 109), (150, 123), (255, 255, 255), 2)
        cv2.rectangle(image_canvas, (152, 105), (252, 125), (0, 0, 0), 2)
    else:
        cv2.rectangle(image_canvas, (50, 109), (150, 123), (0, 0, 0), 2)
        cv2.rectangle(image_canvas, (152, 105), (252, 125), (255, 255, 255), 2)

    frame = detector.findHands(frame, draw=True)
    landmark_list = detector.findPosition(frame, draw=False)

    if len(landmark_list) != 0:
        x1, y1 = (landmark_list[8][1:])  # index
        x2, y2 = landmark_list[12][1:]  # middle
    
        my_fingers = detector.fingerStatus()
        # print(my_fingers)
        if my_fingers[1] and my_fingers[2] and my_fingers[3] and my_fingers[4] and not my_fingers[0]:
            cv2.putText(frame, "Eraser", (1150, 700), fontFace=cv2.FONT_HERSHEY_COMPLEX, color=(255, 255, 0),
                        thickness=2, fontScale=1)
            cv2.line(frame, (x2, y2), (x1, y1), color=(0, 0, 0), thickness=eraser_thickness)
            cv2.line(image_canvas, (x2, y2), (x1, y1), color=(0, 0, 0), thickness=eraser_thickness)

        if my_fingers[1] and my_fingers[0]:
            xp, yp = 0, 0

        if my_fingers[1] and my_fingers[2] and not my_fingers[3]:
            xp, yp = 0, 0
            if y1 < 150:
                if 305 < x1 < 405:
                    default_overlay = overlay_image[0]
                    draw_color = (255, 51, 51)
                elif 405 < x1 < 505:
                    default_overlay = overlay_image[1]
                    draw_color = (0, 128, 255)
                elif 505 < x1 < 605:
                    default_overlay = overlay_image[2]
                    draw_color = (0, 255, 255)
                elif 605 < x1 < 705:
                    default_overlay = overlay_image[3]
                    draw_color = (0, 204, 0)
                elif 705 < x1 < 805:
                    default_overlay = overlay_image[4]
                    draw_color = (51, 51, 255)
                elif 870 < x1 < 980:
                    default_overlay = overlay_image[5]
                    draw_color = (0, 0, 0)
                elif 1140 < x1 < 1278:
                    image_canvas = np.zeros((720, 1280, 3), np.uint8)

            elif 120 < y1 < 170:
                if 52 < x1 < 150:
                    brush_thickness = 10

                elif 151 < x1 < 250:
                    brush_thickness = 15

            cv2.putText(frame, 'Selection Mode', (1000, 700), fontFace=cv2.FONT_HERSHEY_COMPLEX, color=(0, 255, 255), thickness=2, fontScale=1)
            cv2.line(frame, (x1, y1), (x2, y2), color=draw_color, thickness=3)

        if my_fingers[1] and not (my_fingers[2] or my_fingers[0]):
                     
            cv2.circle(frame, (x1, y1), 15, draw_color, thickness=-1)

            if xp == 0 and yp == 0:
                xp = x1
                yp = y1
            
            if draw_color == (0, 0, 0):
                cv2.putText(frame, "Eraser", (1150, 700), fontFace=cv2.FONT_HERSHEY_COMPLEX, color=(255, 255, 0),
                            thickness=2, fontScale=1)
                cv2.line(frame, (xp, yp), (x1, y1), color=draw_color, thickness=eraser_thickness)
                cv2.line(image_canvas, (xp, yp), (x1, y1), color=draw_color, thickness=eraser_thickness)

            else:
                cv2.putText(frame, "Writing Mode", (1000, 700), fontFace=cv2.FONT_HERSHEY_COMPLEX, color=(255, 255, 0),
                            thickness=2, fontScale=1)
                cv2.line(frame, (xp, yp), (x1, y1), color=draw_color, thickness=brush_thickness)
                cv2.line(image_canvas, (xp, yp), (x1, y1), color=draw_color, thickness=brush_thickness)
            
            xp, yp = x1, y1

    img_gray = cv2.cvtColor(image_canvas, cv2.COLOR_BGR2GRAY)
    _, imginv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
    imginv = cv2.cvtColor(imginv, cv2.COLOR_GRAY2BGR)
    frame = cv2.bitwise_and(frame, imginv)
    frame = cv2.bitwise_or(frame, image_canvas)
    currentT = time.time()
    fps = 1/(currentT - previousT)
    previousT = currentT

    cv2.putText(frame, 'Client FPS:' + str(int(fps)), (10, 700), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 0, 0), thickness=2)

    cv2.imshow('paint', frame)
    cv2.waitKey(1)
