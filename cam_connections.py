import cv2 as cv
from functions import *
import subprocess
from time import sleep
from devices_class import devices

class cam_scam(devices):
    def __init__(self):
        subprocess.run(['sudo','modprobe', 'v4l2loopback', f'devices=0'], capture_output=True,text=True)#{','.join(self.virtual_cam_ids)}'])
        self.physical_cams = all_cameras_objects()
        self.delta = len(self.physical_cams)

        self.virtual_cam_ids = []
        self.virtual_cam_processes = []
        self.create_virlual()
        self.unfreeze()

    @staticmethod
    def test(id: int):
        cap = cv.VideoCapture(id)
        show_cam_image(cap)
        cap.release()
        cv.destroyAllWindows()

    def create_virlual(self):
        self.virtual_cam_ids = [str(x) for x in range(self.delta, self.delta * 2)]
        for id in self.virtual_cam_ids:
            subprocess.run(['sudo', 'v4l2loopback-ctl', 'add', f'video{id}'])

    def unfreeze(self):
        for i in range(self.delta):
            print(['ffmpeg', '-i', f'/dev/video{i}', '-vcodec', 'rawvideo', '-pix_fmt', 'yuv420p', '-threads', '0', '-f', 'v4l2', f'/dev/video{i + self.delta}'])
            self.virtual_cam_processes.append(subprocess.Popen(['ffmpeg', '-i', f'/dev/video{i}', '-vcodec', 'rawvideo', '-pix_fmt', 'yuv420p', '-threads', '0', '-f', 'v4l2', f'/dev/video{i + self.delta}'], shell=False, stdout=subprocess.PIPE))
        
    def freeze(self):
        for pr in self.virtual_cam_processes:
            print(['kill', str(pr.pid)])
            subprocess.run(['kill', str(pr.pid)], capture_output=True, text=True)
        self.virtual_cam_processes = []

    def __del__(self):
        self.freeze()
        for index, cam in enumerate(self.physical_cams):
            try:
                cam.release()
            except:
                pass
        print('\033[91mPlease enter this command!')
        print('sudo v4l2loopback-ctl delete /dev/video* ')
        # subprocess.run(['v4l2loopback-ctl', 'delete', f'/dev/video*'], shell=True)


if __name__ == "__main__":
    cam_scam.test(3)