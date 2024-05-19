class SingletonMetaclass(type):
    def __init__(cls, name, bases, attrs):
        super(SingletonMetaclass, cls).__init__(name, bases, attrs)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(SingletonMetaclass, cls).__call__(*args, **kwargs)
        return cls.instance
