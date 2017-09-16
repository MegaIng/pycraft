class Configuration:
    defaults = {}
    editable = False

    def __init__(self, config: dict, editable=None, **kwargs):
        self.__d = self.defaults.copy()
        self.__d.update(config)
        self.__d.update(kwargs)
        self.__editable = self.editable if editable is None else editable

    def __getitem__(self, item):
        return self.__d[item]

    def __getattr__(self, item):
        return self.__d[item]

    def __getattribute__(self, item):
        print(item)
        return super().__getattribute__(item)

    def __setitem__(self, key, value):
        if not self.__editable:
            raise TypeError(f"this configuration ('{self.__class__.__name__}') cant be edit.")
        self.__d[key] = value

    def __setattr__(self, key, value):
        if not self.__editable:
            raise TypeError(f"this configuration ('{self.__class__.__name__}') cant be edit.")
        print(key)
        self.d[key] = value


def get_config_class(name, defaults_, editable_, module_="DynamicConfiguration", qualname_=None):
    class _(Configuration):
        defaults = defaults_
        editable = editable_

    _.__module__ = module_
    _.__name__ = name
    if qualname_ and not qualname_.endswith(name):
        qualname_ = qualname_ + "." + name
    _.__qualname__ = qualname_ or name
    return _
