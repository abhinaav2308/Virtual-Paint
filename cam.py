import cv2
import numpy as np
import os
import track_hands as TH


class VideoCamera():
    def __init__(self, overlay_image=None, draw_color=(255, 51, 51)):
        if overlay_image is None:
            overlay_image = []
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)
        self.xp = 0
        self.yp = 0
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.brush_thickness = 15
        self.eraser_thickness = 30
        self.overlay_image = overlay_image
        self.draw_color = draw_color
        self.detector = TH.handDetector(min_detection_confidence=0.85)
        self.image_canvas = np.zeros((720, 1280, 3), np.uint8)
        self.default_overlay = overlay_image[0]

    def __del__(self):
        self.cap.release()

    def set_overlay(self, frame, overlay_image):
        self.default_overlay = overlay_image[0]
        frame[0:125, 0:1280] = self.default_overlay
        return frame

    def get_frame(self, overlay_image):
        _, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        frame[0:125, 0:1280] = self.default_overlay
        frame = self.detector.findHands(frame, draw=True)
        landmark_list = self.detector.findPosition(frame, draw=False)

        if self.brush_thickness == 10:
            cv2.rectangle(self.image_canvas, (50, 109), (150, 123), (255, 255, 255), 2)
            cv2.rectangle(self.image_canvas, (152, 105), (252, 125), (0, 0, 0), 2)
        else:
            cv2.rectangle(self.image_canvas, (50, 109), (150, 123), (0, 0, 0), 2)
            cv2.rectangle(self.image_canvas, (152, 105), (252, 125), (255, 255, 255), 2)

        if len(landmark_list) != 0:
            self.x1, self.y1 = (landmark_list[8][1:])  # index
            self.x2, self.y2 = landmark_list[12][1:]  # middle

            my_fingers = self.detector.fingerStatus()

            if my_fingers[1] and my_fingers[2] and my_fingers[3] and my_fingers[4] and not my_fingers[0]:
                cv2.putText(frame, "Eraser", (1150, 700), fontFace=cv2.FONT_HERSHEY_COMPLEX, color=(255, 255, 0),
                            thickness=2, fontScale=1)
                cv2.line(frame, (self.x2, self.y2), (self.x1, self.y1), color=(0, 0, 0),
                         thickness=self.eraser_thickness)
                cv2.line(self.image_canvas, (self.x2, self.y2), (self.x1, self.y1), color=(0, 0, 0),
                         thickness=self.eraser_thickness)

            if my_fingers[1] and my_fingers[0]:
                self.xp, self.yp = 0, 0

            if my_fingers[1] and my_fingers[2] and not my_fingers[3]:
                self.xp, self.yp = 0, 0
                if self.y1 < 165:
                    if 305 < self.x1 < 405:
                        self.default_overlay = overlay_image[0]
                        frame[0:125, 0:1280] = self.default_overlay
                        self.draw_color = (255, 51, 51)
                    elif 405 < self.x1 < 505:
                        self.default_overlay = overlay_image[1]
                        self.draw_color = (0, 128, 255)
                        frame[0:125, 0:1280] = self.default_overlay
                    elif 505 < self.x1 < 605:
                        self.default_overlay = overlay_image[2]
                        self.draw_color = (0, 255, 255)
                        frame[0:125, 0:1280] = self.default_overlay
                    elif 605 < self.x1 < 705:
                        self.default_overlay = overlay_image[3]
                        self.draw_color = (0, 204, 0)
                        frame[0:125, 0:1280] = self.default_overlay
                    elif 705 < self.x1 < 805:
                        self.default_overlay = overlay_image[4]
                        self.draw_color = (51, 51, 255)
                        frame[0:125, 0:1280] = self.default_overlay
                    elif 870 < self.x1 < 980:
                        self.default_overlay = overlay_image[5]
                        self.draw_color = (0, 0, 0)
                        frame[0:125, 0:1280] = self.default_overlay
                    elif 1140 < self.x1 < 1278:
                        self.image_canvas = np.zeros((720, 1280, 3), np.uint8)
                        frame[0:125, 0:1280] = self.default_overlay

                elif 120 < self.y1 < 170:
                    if 52 < self.x1 < 150:
                        self.brush_thickness = 10
                    elif 151 < self.x1 < 250:
                        self.brush_thickness = 15

                cv2.putText(frame, 'Selection Mode', (1000, 700), fontFace=cv2.FONT_HERSHEY_COMPLEX,
                            color=(0, 255, 255), thickness=2, fontScale=1)
                cv2.line(frame, (self.x1, self.y1), (self.x2, self.y2), color=self.draw_color, thickness=3)

            if my_fingers[1] and not my_fingers[2] and not my_fingers[0]:

                cv2.circle(frame, (self.x1, self.y1), 15, self.draw_color, thickness=-1)

                if self.xp == 0 and self.yp == 0:
                    self.xp = self.x1
                    self.yp = self.y1

                if self.draw_color == (0, 0, 0):
                    cv2.putText(frame, "Eraser", (1150, 700), fontFace=cv2.FONT_HERSHEY_COMPLEX, color=(255, 255, 0),
                                thickness=2, fontScale=1)
                    cv2.line(frame, (self.xp, self.yp), (self.x1, self.y1), color=self.draw_color,
                             thickness=self.eraser_thickness)
                    cv2.line(self.image_canvas, (self.xp, self.yp), (self.x1, self.y1), color=self.draw_color,
                             thickness=self.eraser_thickness)

                else:
                    cv2.putText(frame, "Writing Mode", (1000, 700), fontFace=cv2.FONT_HERSHEY_COMPLEX,
                                color=(255, 255, 0),
                                thickness=2, fontScale=1)
                    cv2.line(frame, (self.xp, self.yp), (self.x1, self.y1), color=self.draw_color,
                             thickness=self.brush_thickness)
                    cv2.line(self.image_canvas, (self.xp, self.yp), (self.x1, self.y1), color=self.draw_color,
                             thickness=self.brush_thickness)

                self.xp, self.yp = self.x1, self.y1

        frame[0:125, 0:1280] = self.default_overlay
        cv2.putText(frame, 'Air Paint', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, self.draw_color, 5, cv2.LINE_AA)
        cv2.putText(frame, 'Size:', (5, 119), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.rectangle(frame, (50, 109), (150, 121), (0, 0, 0), -1)
        cv2.rectangle(frame, (152, 105), (252, 123), (0, 0, 0), -1)

        img_gray = cv2.cvtColor(self.image_canvas, cv2.COLOR_BGR2GRAY)
        _, imginv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
        imginv = cv2.cvtColor(imginv, cv2.COLOR_GRAY2BGR)
        frame = cv2.bitwise_and(frame, imginv)
        frame = cv2.bitwise_or(frame, self.image_canvas)

        _, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()


def main():
    overlay_image = []
    header_img = "Images"
    header_img_list = os.listdir(header_img)
    for i in header_img_list:
        image = cv2.imread(f'{header_img}/{i}')
        overlay_image.append(image)

    cam1 = VideoCamera(overlay_image=overlay_image)

    while True:
        ret, input_img = cam1.cap.read()
        input_img = cv2.flip(input_img, 1)
        my_frame = cam1.get_frame(frame=input_img, overlay_image=overlay_image)

        cv2.imshow('out', my_frame)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
