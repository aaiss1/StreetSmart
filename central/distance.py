import cv2
import numpy as np
import global_vars

# ------------------------------------------------- #
#                        SETUP                      #
# ------------------------------------------------- #
file = cv2.FileStorage()
file.open('include/stereomapping.xml', cv2.FileStorage_READ)

L_x = file.getNode('left_stereo_map_x').mat()
L_y = file.getNode('left_stereo_map_y').mat()
R_x = file.getNode('right_stereo_map_x').mat()
R_y = file.getNode('right_stereo_map_y').mat()
file.release()

left_capture = cv2.VideoCapture(0)
right_capture = cv2.VideoCapture(1)

min_disparity = 0
max_disparity = 16 * 10
block_size = 7
max_speckle_size = 200

uniqueness_ratio = 10
speckle_window_size = 200
speckle_range = 1

num_channels = 1 # only 1 channel in the image since its a 2D image
p1 = 8 * num_channels * block_size ** 2
p2 = 32 * num_channels * block_size ** 2
stereo = cv2.StereoSGBM_create(minDisparity=min_disparity, numDisparities=(max_disparity - min_disparity), preFilterCap=16, blockSize=block_size, P1=p1, P2=p2, uniquenessRatio=uniqueness_ratio, speckleWindowSize=speckle_window_size, speckleRange=speckle_range, disp12MaxDiff=1)

# # Q matrix from stereorectification - need to be updated if calibration changes
persepctive_trans_mat = np.array([[ 1.00000000,  0.00000000,  0.00000000, -18.14719772], 
                                  [ 0.00000000,  1.00000000, 0.00000000, -232.95205879], 
                                  [ 0.00000000,  0.00000000,  0.00000000,  526.02867126], 
                                  [ 0.00000000,  0.00000000,  4.06116344, -0.00000000]]) 


def check_for_large_obstacles(depth_map, depth_threshold_in_meters):
    mask = cv2.inRange(depth_map, 0, depth_threshold_in_meters) # Filter out depths that are greater depth threshold

    # Check if a significantly large obstacle is present and filter out smaller noisy regions
    if np.sum(mask)/255.0 > 0.01 * mask.shape[0] * mask.shape[1]:
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # Contour detection 
        cnts = sorted(contours, key=cv2.contourArea, reverse=True) # Sort based on size
        
        # Check if largest detected contour is significantly large
        if cv2.contourArea(cnts[0]) > 0.01 * mask.shape[0] * mask.shape[1]:
            return True

    return False

def kill_cameras():
    left_capture.release()
    right_capture.release()
    cv2.destroyAllWindows()
    print("Cameras Off")

def start_distance():
    while not global_vars.kill_distance_thread.is_set():
        if left_capture.isOpened():
            success_left, img_left = left_capture.read()
            success_right, img_right = right_capture.read()
            if success_left and success_right :
                #undistort and recitfy image
                imgR_gray = cv2.cvtColor(img_right, cv2.COLOR_BGR2GRAY)
                imgL_gray = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY)
                left_fixed= cv2.remap(imgL_gray, L_x, L_y, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)
                right_fixed= cv2.remap(imgR_gray, R_x, R_y, cv2.INTER_LANCZOS4, cv2.BORDER_CONSTANT, 0)

                # Determine disparity
                disparity = stereo.compute(left_fixed, right_fixed)
                cv2.filterSpeckles(disparity, 0, max_speckle_size, max_disparity)
                disparity = cv2.normalize(disparity, disparity, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U) # Scaling down the disparity values and normalizing them - need to /16 and convert to float to get true disparity

                # Determine depth by estimating the XYZ coordinates and extracting z
                coordinates3d = cv2.reprojectImageTo3D(disparity, persepctive_trans_mat)
                depth = coordinates3d[:,:,2]
                # np.set_printoptions(threshold=np.inf)
                # print(depth)

                # Perform distance detection
                depth_thresh = 0.7 # Threshold for SAFE distance in meters - experimentally skewed to account for camera inaccuracy
                global_vars.haptic = check_for_large_obstacles(depth_map=depth, depth_threshold_in_meters=depth_thresh)
                    
                cv2.imshow('output_canvas',disparity)

    kill_cameras()


# Main program logic follows:
#This section won't be running during the thread
if __name__ == '__main__':
    try:
        start_distance()
 
    except KeyboardInterrupt:
        kill_cameras()