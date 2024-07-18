class devices:
    def freeze(self):
        pass

    def unfreeze(self):
        pass

    def __del__(self):
        pass

    def release(self):
        self.__del__()