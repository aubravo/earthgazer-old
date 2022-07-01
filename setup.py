

class TEST:
    def __init__(self):
        print(self.__getattr__('__name__'))
        print(self.__dict__)

X = TEST()
