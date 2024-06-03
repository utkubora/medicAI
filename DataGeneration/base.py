class StaticClass:
    def __new__(cls, *args, **kwargs):
        raise NotImplementedError("This class can not be instantiated.")