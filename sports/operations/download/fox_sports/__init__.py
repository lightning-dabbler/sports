class Dispatcher:
    def __init__(self, container_class=None, **kwargs):
        self.container_class = container_class
        self.kwargs = kwargs

    @classmethod
    def dispatch(cls, container_cls, url, set_pull_meta=True, extra_kwargs=None, **kwargs):
        extra_kwargs = extra_kwargs or {}
        container = container_cls.from_request(url, set_pull_meta=set_pull_meta, **kwargs)
        return cls(container_class=container, **extra_kwargs)
