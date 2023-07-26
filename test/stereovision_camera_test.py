import numpy as np
import cv2

file = cv2.FileStorage()
file.open('/home/pi/StreetSmart/test/include/stereomapping.xml', cv2.FileStorage_READ)

L_x = file.getNode('left_stereo_map_x').mat()
L_y = file.getNode('left_stereo_map_y').mat()
R_x = file.getNode('right_stereo_map_x').mat()
R_y = file.getNode('right_stereo_map_y').mat()

left_capture = cv2.VideoCapture(2)
right_capture = cv2.VideoCapture(0)

while left_capture.isOpened():
    success_left, img_left = left_capture.read()
    success_right, img_right = right_capture.read()
    # print(success_left + success_right)
    cv2.imshow('original left camera', img_left)
    cv2.imshow('original right camera', img_right)
    if success_left and success_right :
        #undistort and recitfy image
        left_fixed= cv2.remap(img_left, L_x, L_y, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
        right_fixed= cv2.remap(img_right, R_x, R_y, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
        
        cv2.imshow('fixed left camera', left_fixed)
        cv2.imshow('fixed right camera', right_fixed)
        

    key = cv2.waitKey(5)
    if key == ord('q'):
        break

left_capture.release()
right_capture.release()
cv2.destroyAllWindows()
