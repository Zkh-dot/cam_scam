import cv2
from functions import *
import subprocess
from time import sleep
from abstract_classes import device, devices
import sys
import numpy as np
import os

class camera(device):
    def __init__(self, cam_id: int, delta: int):
        self.id = cam_id
        self.delta = delta
        self.current_stream = None
        self.current_stream_type = "None"
        # TODO: write blank funcs for released objcts
        self.released = False
        subprocess.run(['sudo', 'v4l2loopback-ctl', 'add', f'video{id}'])

    
    def stop_stream(self):
        if self.current_stream:
            subprocess.run(['kill', str(self.current_stream.pid)])

    def create_video(self):
        print(f'video from cam {self.delta + self.id}')
        try:
            height, width, channels = self.image.shape
            video_format = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(f'./videos/cam-{self.delta + self.id}.mp4', fourcc=video_format, fps=2, frameSize=(width, height))
            for ii in range(self.im_quantity):
                video.write(sp_noise(self.image, self.noise_prob))
            video.release()
        except Exception as e:
            print(f"who cares about video from cam {self.delta + self.id}")
            print(e)

    def create_photo(self):
        try:
            self.image = cv2.VideoCapture(self.delta + self.id).read()[1]
            cv2.imwrite(f'./pictures/cam-{self.delta + self.id}.png', self.image)
            cv2.imwrite(f'./pictures/cam-{self.delta + self.id}-n.png', sp_noise(self.image))
        except:
            print(f'who cares about cam {self.delta + self.id}')
            self.released = True

    def stream_camera(self):
        self.stop_stream()
        self.current_stream_type = "camera"
        self.current_stream = subprocess.Popen(['ffmpeg', '-i', f'/dev/video{self.id}', '-vcodec', 'rawvideo', '-pix_fmt', 'yuv420p', '-threads', '0', '-f', 'v4l2', f'/dev/video{self.id + self.delta}'], shell=False)
    
    def stream_picture(self):
        self.current_stream_type = "picture"
        self.create_photo()
        self.stop_stream()
        self.current_stream = subprocess.Popen(['ffmpeg', '-i', f'./pictures/cam-{self.delta + self.id}-n.png', '-vcodec', 'rawvideo', '-pix_fmt', 'yuv420p', '-threads', '0', '-f', 'v4l2', f'/dev/video{self.id + self.delta}'], shell=False)

    def stream_noisy_video(self):
        self.current_stream_type = "video"
        self.create_video()
        self.stop_stream()
        self.current_stream = subprocess.Popen(['ffmpeg', '-stream_loop', '100000', '-i', f'./videos/cam-{self.delta + self.id}.mp4', '-filter:v', 'fps=1', '-map', '0:v','-f', 'v4l2', f'/dev/video{self.id + self.delta}'], shell=False)

    def freeze(self):
        self.stream_picture()
        self.stream_noisy_video()

    def release(self):
        self.__del__()

    def __del__(self):
        self.stop_all_streams()
        try:
            print(' '.join(['sudo', 'v4l2loopback-ctl', 'delete', '/dev/video' + str(self.delta + self.id)]))
            subprocess.run(['sudo', 'v4l2loopback-ctl', 'delete', '/dev/video' + str(self.delta + self.id)])
        except ImportError:
            pass
        except Exception as e:
            print(e)
        

# TODO: refactor using camera class
class cam_scam(devices):
    def __init__(self, noise_prob=0.001, delay=0):
        print("===== noise", noise_prob)
        subprocess.run(['sudo','modprobe', 'v4l2loopback', f'devices=0'], capture_output=True,text=True)#{','.join(self.virtual_cam_ids)}'])
        self.physical_cams = all_cameras_objects()
        self.delta = len(self.physical_cams)
        self.noise_prob = noise_prob
        self.im_quantity = 10
        self.__delay = delay

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
            print(['kill', str(pr.pid)])
            subprocess.run(['kill', str(pr.pid)])
            try:
                msg, image = cv2.VideoCapture(i).read()
                height, width, channels = image.shape
                os.chdir('./pictures')
                cv2.imwrite(f'./pictures/cam-{self.delta + i}.png', image)
                image = cv2.GaussianBlur(image, (int(height)-1,int(width)-1), self.noise_prob)
                # image = cv2.imdecode(np.frombuffer(sp_noise(image, self.noise_prob), np.uint8), cv2.IMREAD_UNCHANGED)
                cv2.imwrite(f'./pictures/cam-{self.delta + i}-n.png', image)
            except Exception as e:
                print(f'---who cares about cam {self.delta + i}---')
                print('---', e, 'in', e.__traceback__.tb_lineno, '---')


            # TODO: doesnt work (i guess)
            temp_array.append(subprocess.Popen(['ffmpeg', '-i', f'./pictures/cam-{self.delta + i}-n.png', '-vcodec', 'rawvideo', '-pix_fmt', 'yuv420p', '-threads', '0', '-f', 'v4l2', f'/dev/video{i + self.delta}'], shell=False))
        self.virtual_cam_processes = temp_array

    def video_translation(self):
        temp_array = []
        for i, pr in enumerate(self.virtual_cam_processes):
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
            subprocess.run(['sudo', 'rm', '-rf' './pictures/*'])
        self.virtual_cam_processes = temp_array

    def freeze(self):
        sleep(self.__delay)
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