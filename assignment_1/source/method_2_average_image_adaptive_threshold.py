# Program to find smears on camera lens by averaging multiple photo's worth of
#   pixel values and using thresholding techniques in openCV

# Use by going to directory which holds "sample_drive" and entering which
#   camera to use. (0-3, 5) as the second argument.

import sys
import numpy as np
import cv2
import os

def find_mean_img(file_list):
    # parameter for number of photos to test
    test_size = 301

    # create a matrix to store the pixel values after resize
    mean_matrix = np.zeros((1000,1000,3),np.float)

    # reseize each image and store pixel value
    print('Processing...')
    image_count = 0;
    while image_count < len(file_list):
        img = cv2.imread(photo_dir_path+file_list[image_count])
        img = cv2.resize(img,(1000,1000))
        img = cv2.GaussianBlur(img,(5,5),0)
        img_matrix = np.array(img, dtype=np.float)
        mean_matrix += img_matrix
        image_count += (len(file_list) / test_size)

    # find avg pixel values
    mean_matrix = mean_matrix / (test_size)
    mean_matrix = np.array(np.round(mean_matrix),dtype=np.uint8)

    cv2.imwrite('cam_'+str(cam)+"_mean.jpg",mean_matrix)
    return mean_matrix

def create_mask(mean_img):
    # cv2.adaptiveThreshold parameters
    thresh_block_size = 101
    subtracted_constant = 6

    # Convert mean image to grayscale
    gray = cv2.cvtColor(mean_img,cv2.COLOR_BGR2GRAY)
    mean_matrix = np.array(np.round(gray),dtype=np.uint8)

    # Binarize image with adaptiveThreshold
    mean_thresh = cv2.adaptiveThreshold(mean_matrix,255,\
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,\
    thresh_block_size, subtracted_constant)

    return mean_thresh

def show_smudge(mask_img):
    # contour size limits
    min_cnt_area = 500
    max_cnt_area = 3000

    # Pull random image
    rand_number = np.random.randint(low=0, high=len(file_list))
    rand_img = cv2.imread(photo_dir_path+file_list[rand_number])
    rand_img = cv2.resize(rand_img,(1000,1000))

    # find the contours on the mask and check for appropriate size
    _,contours,hierarchy = cv2.findContours(mask_img, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    # print(hierarchy[0])
    cnt_count = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # print(area)
        if area > min_cnt_area and area < max_cnt_area:
            # draw smudge on random image
            rand_img = cv2.drawContours(rand_img,cnt,-1,(0,255,0),3)
            cv2.imwrite('cam_'+str(cam)+"_found.jpg",rand_img)
            cnt_count += 1
    if cnt_count == 0:
        print("No Smudge Found")
    else:
        print("Found Smudge")


if __name__ == "__main__":
    # check for correct number of arguments
    if len(sys.argv) != 2:
        print('Enter which camera to use. (0-3, 5) as second argument.')
        sys.exit()
    cam = int(sys.argv[1])
    if not cam in (0,1,2,3,5):
        print('Enter which camera to use. (0-3, 5) as second argument.')
        sys.exit()

    # Make a list of photo names
    photo_dir_path = "sample_drive/cam_" + str(cam) + "/"
    file_list = os.listdir(photo_dir_path)

    mean_image = find_mean_img(file_list)
    mask = create_mask(mean_image)
    cv2.imwrite('cam_'+str(cam)+"_mask.jpg",mask)
    show_smudge(mask)
