import cv2
import subprocess
from time import sleep
import sys
import numpy as np
import os
import re
from abstract_classes import device, devices
from functions import *
from singleton_logger import Logger

logger = Logger().get_logger()

class camera(device):
    def __init__(self, cam_id: int, delta: int, noise_prob: float, im_quantity: int = 10):
        if not type(cam_id) == int or not  type(delta) == int:
            raise TypeError("not integer input to camera obj!")
        self.id = cam_id
        self.delta = delta
        self.noise_prob = noise_prob
        self.current_stream = None
        self.im_quantity = im_quantity
        self.current_stream_type = "None"
        # TODO: write blank funcs for _released objcts
        self._released = False
        subprocess.run(['sudo', 'v4l2loopback-ctl', 'add', f'video{id}'])
    
    def _stop_stream(self):
        logger.info(f"camera {self.id} - stop stream")
        if self.current_stream:
            subprocess.run(['kill', str(self.current_stream.pid)])

    def _create_video(self):
        logger.info(f"camera {self.id} - create video")
        try:
            height, width, channels = self.image.shape
            video_format = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(f'./src/videos/cam-{self.delta + self.id}.mp4', fourcc=video_format, fps=1, frameSize=(width, height))
            for ii in range(self.im_quantity):
                video.write(sp_noise(self.image, self.noise_prob))
            video._release()
            logger.info(f"camera {self.id} - video created")
        except Exception as e:
            logger.error(f"camera {self.id} - {str(e)}, {__file__}, {e.__traceback__.tb_lineno} ---")

    def _create_photo(self):
        logger.info(f"camera {self.id} - create photo")
        try:
            self.image = cv2.VideoCapture(self.delta + self.id).read()[1]
            logger.debug(f"camera {self.id} - image " + str(type(self.image)))
            cv2.imwrite(f'./src/pictures/cam-{self.delta + self.id}.png', self.image)
            cv2.imwrite(f'./src/pictures/cam-{self.delta + self.id}-n.png', sp_noise(self.image, self.noise_prob))
            logger.info(f"photoes ./src/pictures/cam-{self.delta + self.id}.png created")
        except Exception as e:
            logger.error(f"camera {self.id} - {str(e)}, {__file__}, {e.__traceback__.tb_lineno} ---")
            self._released = True

    def _stream_camera(self):
        logger.info(f"camera {self.id} - stream camera")
        try:
            self._stop_stream()
            self.current_stream_type = "camera"
            self.current_stream = subprocess.Popen(['ffmpeg', '-i', f'/dev/video{self.id}', '-vcodec', 'rawvideo', '-pix_fmt', 'yuv420p', '-threads', '0', '-f', 'v4l2', f'/dev/video{self.id + self.delta}'], shell=False)
        except Exception as e:
            logger.error(f"camera {self.id} - {str(e)}, {__file__}, {e.__traceback__.tb_lineno} ---")


    def _stream_picture(self):
        logger.info(f"camera {self.id} - stream picture")
        self.current_stream_type = "picture"
        self._create_photo()
        self._stop_stream()
        self.current_stream = subprocess.Popen(['ffmpeg', '-i', f'./src/pictures/cam-{self.delta + self.id}-n.png', '-vcodec', 'rawvideo', '-pix_fmt', 'yuv420p', '-threads', '0', '-f', 'v4l2', f'/dev/video{self.id + self.delta}'], shell=False)

    def _stream_noisy_video(self):
        logger.info(f"camera {self.id} - stream noisy video")
        self.current_stream_type = "video"
        self._create_video()
        self._stop_stream()
        self.current_stream = subprocess.Popen(['ffmpeg', '-stream_loop', '100000', '-i', f'./src/videos/cam-{self.delta + self.id}.mp4', '-filter:v', 'fps=1', '-map', '0:v','-f', 'v4l2', f'/dev/video{self.id + self.delta}'], shell=False)

    def freeze(self):
        logger.info(f"camera {self.id} - freeze")
        self._stream_picture()
        self._stream_noisy_video()

    def unfreeze(self):
        logger.info(f"camera {self.id} - unfreeze")
        self._stream_camera()

    def _release(self):
        self.__del__()

    def __del__(self):
        try:
            self._stop_stream()
            # a bit of time to release camera
            sleep(1)
            print(' '.join(['sudo', 'v4l2loopback-ctl', 'delete', '/dev/video' + str(self.delta + self.id)]))
            subprocess.run(['sudo', 'v4l2loopback-ctl', 'delete', '/dev/video' + str(self.delta + self.id)])
        except ImportError:
            pass
        except Exception as e:
            print(e)
        

class new_cam_scam(devices):
    def __init__(self, noize_prob=0.001, delay=0) -> None:
        subprocess.run(['sudo','modprobe', 'v4l2loopback', f'devices=0'], capture_output=True,text=True)#{','.join(self.virtual_cam_ids)}'])
        self.physical_cam_names = all_cam_names()
        self.delay = delay
        self.delta = len(self.physical_cam_names)
        self.virtual_cams = [camera(int(re.match(r".*?video(\d*)", cam_name)[1]), self.delta, noize_prob) for cam_name in self.physical_cam_names]
        self.unfreeze()

    def _freeze_all_cams(self):
        for id in range(len(self.virtual_cams)):
            self.virtual_cams[id].freeze()

    def _unfreeze_all_cams(self):
        for id in range(len(self.virtual_cams)):
            self.virtual_cams[id].unfreeze()

    def freeze(self):
        sleep(self.delay)
        self._freeze_all_cams()

    def unfreeze(self):
        sleep(self.delay)
        self._unfreeze_all_cams()

    def _release(self):
        for id in range(len(self.virtual_cams)):
            self.virtual_cams[id]._release()

    def __del__(self):
        self._release()




# basicly outdated code, can be deleted
class cam_scam(devices):
    def __init__(self, noise_prob=0.001, delay=0):
        print("===== noise", noise_prob)
        subprocess.run(['sudo','modprobe', 'v4l2loopback', f'devices=0'], capture_output=True,text=True)#{','.join(self.virtual_cam_ids)}'])
        self.physical_cams = all_cam_names()
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
                os.chdir('./src/pictures')
                cv2.imwrite(f'./src/pictures/cam-{self.delta + i}.png', image)
                image = cv2.GaussianBlur(image, (int(height)-1,int(width)-1), self.noise_prob)
                # image = cv2.imdecode(np.frombuffer(sp_noise(image, self.noise_prob), np.uint8), cv2.IMREAD_UNCHANGED)
                cv2.imwrite(f'./src/pictures/cam-{self.delta + i}-n.png', image)
            except Exception as e:
                print(f'---who cares about cam {self.delta + i}---')
                print('---', e, 'in', e.__traceback__.tb_lineno, '---')


            # TODO: doesnt work (i guess)
            temp_array.append(subprocess.Popen(['ffmpeg', '-i', f'./src/pictures/cam-{self.delta + i}-n.png', '-vcodec', 'rawvideo', '-pix_fmt', 'yuv420p', '-threads', '0', '-f', 'v4l2', f'/dev/video{i + self.delta}'], shell=False))
        self.virtual_cam_processes = temp_array

    def video_translation(self):
        temp_array = []
        for i, pr in enumerate(self.virtual_cam_processes):
            print(f'video from cam {self.delta + i}')
            try:
                image = cv2.imread(f'./src/pictures/cam-{self.delta + i}.png')
                height, width, channels = image.shape
                video_format = cv2.VideoWriter_fourcc(*'mp4v')
                video = cv2.VideoWriter(f'./src/videos/cam-{self.delta + i}.mp4', fourcc=video_format, fps=2, frameSize=(width, height))
                for ii in range(self.im_quantity):
                    video.write(sp_noise(image, self.noise_prob))
                video._release()

                print(['kill', str(pr.pid)])
                subprocess.run(['kill', str(pr.pid)])
                temp_array.append(subprocess.Popen(['ffmpeg', '-stream_loop', '100000', '-i', f'./src/videos/cam-{self.delta + i}.mp4', '-filter:v', 'fps=1', '-map', '0:v','-f', 'v4l2', f'/dev/video{i + self.delta}'], shell=False))
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
            subprocess.run(['sudo', 'rm', '-rf' './src/pictures/*'])
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