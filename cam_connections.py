import cv2
from functions import *
import subprocess
from time import sleep
from devices_class import devices
import sys

class cam_scam(devices):
    def __init__(self, noise_prob=0.05):
        subprocess.run(['sudo','modprobe', 'v4l2loopback', f'devices=0'], capture_output=True,text=True)#{','.join(self.virtual_cam_ids)}'])
        self.physical_cams = all_cameras_objects()
        self.delta = len(self.physical_cams)
        self.noise_prob = noise_prob
        self.im_quantity = 10

        self.virtual_cam_ids = []
        self.virtual_cam_processes = []
        self.create_virlual()
        self.unfreeze()

    @staticmethod
    def test(id: int):
        cap = cv2.VideoCapture(id)
        show_cam_image(cap)
        cap.release()
        cv2.destroyAllWindows()

    def create_virlual(self):
        self.virtual_cam_ids = [str(x) for x in range(self.delta, self.delta * 2)]
        for id in self.virtual_cam_ids:
            subprocess.run(['sudo', 'v4l2loopback-ctl', 'add', f'video{id}'])

    def picture_translation(self):
        temp_array = []
        for i, pr in enumerate(self.virtual_cam_processes):
            try:
                image = cv2.VideoCapture(self.delta + i).read()[1]
                cv2.imwrite(f'./pictures/cam-{self.delta + i}.png', image)
                image = sp_noise(image, self.noise_prob)
            except:
                print(f'who cares about cam {self.delta + i}')

            print(['kill', str(pr.pid)])
            subprocess.run(['kill', str(pr.pid)])
            temp_array.append(subprocess.Popen(['ffmpeg', '-i', f'./pictures/cam-{self.delta + i}.png', '-vcodec', 'rawvideo', '-pix_fmt', 'yuv420p', '-threads', '0', '-f', 'v4l2', f'/dev/video{i + self.delta}'], shell=False))
        self.virtual_cam_processes = temp_array

    def video_translation(self):
        temp_array = []
        for i, pr in enumerate(self.virtual_cam_processes):
            # TODO: create video
            print(f'video from cam {self.delta + i}')
            try:
                image = cv2.imread(f'./pictures/cam-{self.delta + i}.png')
                height, width, channels = image.shape
                video_format = cv2.VideoWriter_fourcc(*'mp4v')
                video = cv2.VideoWriter(f'./videos/cam-{self.delta + i}.mp4', fourcc=video_format, fps=2, frameSize=(width, height))
                for ii in range(self.im_quantity):
                    video.write(sp_noise(image, self.noise_prob))
                video.release()

                print(['kill', str(pr.pid)])
                subprocess.run(['kill', str(pr.pid)])
                temp_array.append(subprocess.Popen(['ffmpeg', '-stream_loop', '100000', '-i', f'./videos/cam-{self.delta + i}.mp4', '-filter:v', 'fps=1', '-map', '0:v','-f', 'v4l2', f'/dev/video{i + self.delta}'], shell=False))
            except Exception as e:
                print(f"who cares about video from cam {self.delta + i}")
                print(e)
        self.virtual_cam_processes = temp_array

    def unfreeze(self):
        temp_array = []
        for i in range(self.delta):
            if len(self.virtual_cam_processes) > i:
                print(['kill', str(self.virtual_cam_processes[i].pid)])
                subprocess.run(['kill', str(self.virtual_cam_processes[i].pid)])
            print(['ffmpeg', '-i', f'/dev/video{i}', '-vcodec', 'rawvideo', '-pix_fmt', 'yuv420p', '-threads', '0', '-f', 'v4l2', f'/dev/video{i + self.delta}'])
            temp_array.append(subprocess.Popen(['ffmpeg', '-i', f'/dev/video{i}', '-vcodec', 'rawvideo', '-pix_fmt', 'yuv420p', '-threads', '0', '-f', 'v4l2', f'/dev/video{i + self.delta}'], shell=False))
        self.virtual_cam_processes = temp_array

    def freeze(self):
        self.picture_translation()
        self.video_translation()

    def stop_all_streams(self):
        for i, pr in enumerate(self.virtual_cam_processes):
            print(['kill', str(pr.pid)])
            with open('./logs/ffmpeg.log', 'a') as f:
                subprocess.run(['kill', str(pr.pid)], stdout=f)
            
        self.virtual_cam_processes = []


    def __del__(self):
        self.stop_all_streams()
        for i, cam in enumerate(self.physical_cams):
            try:
                print(' '.join(['sudo', 'v4l2loopback-ctl', 'delete', '/dev/video' + str(self.delta + i)]))
                subprocess.run(['sudo', 'v4l2loopback-ctl', 'delete', '/dev/video' + str(self.delta + i)])
            except ImportError:
                pass
            except Exception as e:
                print(e)
        # print('\033[91mPlease enter this command!')
        # print('sudo v4l2loopback-ctl delete /dev/video*')


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cam_scam.test(int(sys.argv[1]))
    else:
        print('no camera id passed')