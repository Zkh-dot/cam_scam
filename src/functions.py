import cv2 
import subprocess
import glob
import numpy as np
import random

def all_cam_names() -> list:
    return glob.glob('/dev/video*')

def get_picture(cam, index):
    ret, frame = cam.read()
    cv2.imwrite(f'./images/im_{index}.png', frame)

def overvrite_pic():
    with open('/home/scv/image.png', 'rb') as old_file:
        with open('/home/scv/image_1.png', 'rb+') as new_file:
            context = old_file.read()
            new_file.write(context)

def show_cam_image(cap):
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    while True:
        ret, frame = cap.read()
        # if not ret:
        #     print("Can't receive frame (stream end?). Exiting ...")
        #     break
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == ord('q'):
            break


def sp_noise(image: cv2.UMat, prob: float = 0.001):
    '''
    Add salt and pepper noise to image
    prob: Probability of the noise
    '''
    output = np.zeros(image.shape,np.uint8)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            rdn = random.random()
            if rdn < prob:
                if random.randint(0, 1) == 0:
                    output[i][j] = 0
                else:
                    output[i][j] = 255
            else:
                output[i][j] = image[i][j]
    
    return output


if __name__ == '__main__':
    overvrite_pic()