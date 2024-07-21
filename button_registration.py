from pynput.keyboard import Key, Listener
from cam_connections import cam_scam
from micro import MicroScam
from abstract_classes import devices
import sys

class state_manager():
    def __init__(self, button='f12', delay='0', devices="all", mic_id=None, audio_file=None, noise_prob='0.05'):
        self.__devices = {}

        if devices == "all":
            self.__devices['cam'] = cam_scam(float(noise_prob), int(delay))
            self.__devices['mic'] = MicroScam(mic_id, audio_file, int(delay))
        elif devices == "mic":
            self.__devices['mic'] = MicroScam(mic_id, audio_file, int(delay))
        elif devices == "cam":
            self.__devices['cam'] = cam_scam(float(noise_prob), int(delay))
        
        self.__cams_on = True
        self.__button = button
        print('Video devices ready. Please be careful when choosing!')

    @staticmethod
    def test(key: Key):
        print(key.__dict__)
        if(key == Key.f12):
            print('fuck!')

    @property
    def cams_on(self):
        return self.__cams_on

    def change(self):
        if self.__cams_on:
            for key in self.__devices:
                self.__devices[key].freeze()
            self.__cams_on = False
        else:
            for key in self.__devices:
                self.__devices[key].unfreeze()
            self.__cams_on = True

    def check_key(self, key: Key):
        if "name" in key.__dict__ and key.name == self.__button:
            self.change()
        elif self.__button in key.__dict__:
            self.change()
        elif "_name_" in key.__dict__ and key._name_ == self.__button:
            self.change()

    def release(self):
        self.__del__()
    
    def __del__(self):
        for key in self.__devices:
            self.__devices[key].release()


if __name__ == "__main__":
    try:
        manager = state_manager(*sys.argv[1:])
        with Listener(on_press=manager.check_key) as listener:
            listener.join()
    except KeyboardInterrupt:
        print("exiting...")
        manager.release()
    except Exception as e:
        print(e)
