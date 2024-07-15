from pynput.keyboard import Key, Listener
from cam_connections import cam_scam


class state_manager():
    def __init__(self):
        self.__cam_scam = cam_scam()
        self.__cams_on = True
        print('Video devices ready. Please be careful when choosing!')

    @property
    def cams_on(self):
        return self.__cams_on

    def change(self):
        if self.__cams_on:
            self.__cam_scam.disconnect_virtual()
            self.__cams_on = False
        else:
            self.__cam_scam.connect_virtual()
            self.__cams_on = True

    def check_key(self, key: Key):
        if key.name == 'f12':
            self.change()


if __name__ == "__main__":
    manager = state_manager()
    with Listener(on_press=manager.check_key) as listener:
        listener.join()