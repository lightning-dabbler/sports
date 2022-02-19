class Dispatcher:
    def __init__(self, container_class=None, extra_kwargs=None, **kwargs):
        self.container_class = container_class
        self.extra_kwargs = extra_kwargs or {}

    @classmethod
    def dispatch(
        cls, container_cls, url, extra_kwargs=None, set_pull_metadata=True, request_kwargs=None, metadata=None, **kwargs
    ):
        container = container_cls.from_request(
            url, set_pull_metadata=set_pull_metadata, request_kwargs=request_kwargs, metadata=metadata, **kwargs
        )
        return cls(container_class=container, extra_kwargs=extra_kwargs)
