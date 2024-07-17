from pynput.keyboard import Key, Listener
from cam_connections import cam_scam
from micro import MicroScam
import sys

class state_manager():
    def __init__(self, mic_id, audio_file, button):
        self.__cam_scam = cam_scam()
        self.__mic_scam = MicroScam(mic_id, audio_file)
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
            self.__cam_scam.disconnect_virtual()
            self.__mic_scam.freeze()
            self.__cams_on = False
        else:
            self.__cam_scam.connect_virtual()
            self.__mic_scam.unfreeze()
            self.__cams_on = True

    def check_key(self, key: Key):
        if "name" in key.__dict__ and key.name == self.__button:
            self.change()
        elif self.__button in key.__dict__:
            self.change()
        elif "_name_" in key.__dict__ and key._name_ == self.__button:
            self.change()
    
    def __del__(self):
        print(1)
        self.__cam_scam.__del__()
        self.__mic_scam.__del__()

if __name__ == "__main__":
    try:
        manager = state_manager(sys.argv[1], sys.argv[2], sys.argv[3])
        with Listener(on_press=manager.check_key) as listener:
            listener.join()
    except KeyboardInterrupt:
        del manager
