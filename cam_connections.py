import cv2 as cv
from functions import *
import subprocess
from time import sleep

class cam_scam():
    def __init__(self):
        print(['sudo', 'modprobe', 'v4l2loopback', f'devices=0'])
        subprocess.run(['sudo','modprobe', 'v4l2loopback', f'devices=0'], capture_output=True,text=True)#{','.join(self.virtual_cam_ids)}'])
        self.physical_cams = all_cameras_objects()
        self.delta = len(self.physical_cams)
        print('delta ----->', self.delta)
        self.virtual_cam_ids = []
        self.virtual_cam_processes = []
        self.create_virlual()
        sleep(2)
        self.connect_virtual()

    @staticmethod
    def test():
        cap = cv.VideoCapture(1)
        show_cam_image(cap)
        cap.release()
        cv.destroyAllWindows()

    def create_virlual(self):
        self.virtual_cam_ids = [str(x) for x in range(self.delta, self.delta * 2)]
        for id in self.virtual_cam_ids:
            subprocess.run(['sudo', 'v4l2loopback-ctl', 'add', f'video{id}'])

    def connect_virtual(self):
        for i in range(self.delta):
            print(['ffmpeg', '-i', f'/dev/video{i}', '-vcodec', 'rawvideo', '-pix_fmt', 'yuv420p', '-threads', '0', '-f', 'v4l2', f'/dev/video{i + self.delta}'])
            self.virtual_cam_processes.append(subprocess.Popen(['ffmpeg', '-i', f'/dev/video{i}', '-vcodec', 'rawvideo', '-pix_fmt', 'yuv420p', '-threads', '0', '-f', 'v4l2', f'/dev/video{i + self.delta}'], shell=False, stdout=subprocess.PIPE))
        
    def disconnect_virtual(self):
        for pr in self.virtual_cam_processes:
            print(['kill', str(pr.pid)])
            subprocess.run(['kill', str(pr.pid)], capture_output=True, text=True)
        self.virtual_cam_processes = []

    def __del__(self):
        for index, cam in enumerate(self.physical_cams):
            subprocess.run(['v4l2loopback-ctl', 'delete', f'/dev/video{self.delta + index}'])
            cam.release()

if __name__ == "__main__":
    worker = cam_scam()
    # sleep(30)
    # cam_scam.test()
    sleep(20)
    print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    worker.disconnect_virtual()
    # sleep(10)
    # worker.connect_virtual()