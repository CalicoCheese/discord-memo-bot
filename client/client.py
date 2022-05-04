import asyncio
import discord
import os
import sys
import inspect
import importlib
import importlib.util
from typing import Dict, List, Any
from _types import coroutineFunction


class Client(discord.Client):
    def __init__(
            self,
            intents: discord.Intents = discord.Intents.default()
    ):
        super(Client, self).__init__(intents=intents)
        self._extra_events: Dict[str, List[coroutineFunction]] = {}
        self._extensions: Dict[str, Any] = {}
        self._listener_of_group = []

    def dispatch(self, event: str, /, *args: Any, **kwargs: Any):
        super().dispatch(event, *args, **kwargs)
        event_name = "on_" + event
        for func in self._extra_events.get(event_name, []):
            self._schedule_event(func, event_name, *args, **kwargs)
        return

    def add_listener(self, func, name=None):
        name = name or func.__name__
        if not asyncio.iscoroutinefunction(func):
            raise TypeError('Listeners must be coroutines')

        if name in self._extra_events:
            self._extra_events[name].append(func)
        else:
            self._extra_events[name] = []
        return

    def remove_listener(self, func, name=None):
        name = name or func.__name__

        self._extra_events[name].remove(func)
        return

    @staticmethod
    def _resolve_name(name, package):
        try:
            return importlib.util.resolve_name(name, package)
        except ImportError:
            raise ImportError('Extension {0} could not be loaded.'.format(name))

    def load_extension(self, name, *, package=None):
        name = self._resolve_name(name, package)
        if name in self._extensions:
            raise ImportError("Extension {0} is already loaded.".format(name))
        spec = importlib.util.find_spec(name)
        if spec is None:
            raise ImportError("Extension {0} is Not Found".format(name))

        self._load_from_module_spec(spec, name)

    def _load_from_module_spec(self, spec, name):
        lib = importlib.util.module_from_spec(spec)
        sys.modules[name] = lib
        try:
            spec.loader.exec_module(lib)  # type: ignore
        except Exception as e:
            del sys.modules[name]
            raise ImportError("Extension Failed: {0} ({1})".format(name, e.__class__.__name__))

        try:
            setup = getattr(lib, 'setup')
        except AttributeError:
            del sys.modules[name]
            raise ImportError("No Entry Point Error: {0}".format(name))

        try:
            setup(self)
        except Exception as e:
            del sys.modules[name]
            raise ImportError("Extension Failed: {0} ({1})".format(name, e.__class__.__name__))
        else:
            self._extensions[name] = setup
        return

    def load_extensions(self, package: str, directory: str = None) -> None:
        if directory is not None:
            _package = os.path.join(directory, package)
        else:
            _package = package
        logs = [
            "{0}.{1}".format(package, file[:-3])
            for file in os.listdir(_package)
            if file.endswith(".py")
        ]
        for listener_of_group in logs:
            self.load_extension(listener_of_group)
        return

    def add_listener_of_group(self, listener_of_group):
        self._listener_of_group.append(listener_of_group)
        for func, attr in inspect.getmembers(listener_of_group):
            if inspect.iscoroutinefunction(attr):
                if hasattr(attr, '__listener__') and hasattr(attr, '__listener_names__'):
                    if not attr.__listener__:
                        continue
                    for name in attr.__listener_names__:
                        self.add_listener(attr, name=name)
        return
