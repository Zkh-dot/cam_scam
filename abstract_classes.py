class devices:
    def freeze(self):
        pass

    def unfreeze(self):
        pass

    def __del__(self):
        pass

    def release(self):
        self.__del__()

class device:
    def stop_stream(self):
        pass

    def start_stream(self):
        pass