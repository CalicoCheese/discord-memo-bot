import asyncio


def listeners(name: str = None):
    def decorator(func):
        _function = func
        if isinstance(func, staticmethod):
            _function = func.__func__

        if not asyncio.iscoroutinefunction(_function):
            raise TypeError('Listener function must be a coroutine function.')
        _function.__listener__ = True
        if not hasattr(_function, "__listener_names__"):
            _function.__listener_names__ = []
        _function.__listener_names__.append(name)
        return
    return decorator
