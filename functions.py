import cv2 
import subprocess

def all_cameras_objects() -> list:
    index = 0
    arr = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            arr.append(index)
        cap.release()
        index += 1
    return arr

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
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == ord('q'):
            break


if __name__ == '__main__':
    overvrite_pic()