import tempfile
import os

import diskcache

# Use this method on a FanoutCache object to memoize function output
memoized_result = diskcache.fanout.memoize


class CacheManager():
    def __init__(self, storage_path=None):
        if storage_path:
            if os.path.isdir(storage_path):
                raise FileNotFoundError('The provided path is not a valid directory!')
            self.tempdir = os.path.abspath(storage_path)
        else:
            self.tempdir = tempfile.gettempdir()

        self._global_cache = self._build_global_cache()
        self._arenas = {}

    def _build_global_cache(self):
        return GlobalCache(self.tempdir)

    @property
    def global_cache(self):
        return self._global_cache

    def create_arena(self, arena_name):
        if arena_name not in self._arenas:
            self._arenas[arena_name] = CacheArena(self.tempdir, arena_name)

    def remove_arena(self, arena_name):
        return self._arenas.pop(arena_name, None) is not None

    def cleanup(self):
        del self._global_cache
        self._arenas.clear()


class GlobalCache(diskcache.Index):
    """Represents a persistent key-value cache for global usage."""

    def __init__(self, directory, *args, **kwargs):
        super().__init__(directory=directory, *args, **kwargs)


class CacheArena():
    """Represents a cache manager for a specific COG"""

    def __init__(self, directory, name):
        self.directory = os.path.join(directory, name)
        self.name = name
        self._caches = []

    def build_index(self, *args, **kwargs):
        """Returns a persistent key-value cache"""
        # Dissalow passing directory to the constructor
        kwargs.pop('directory', None)
        cache = diskcache.Index(directory=self.directory, *args, **kwargs)
        self._caches.append(cache)
        return cache

    def build_fanout(self, *args, **kwargs):
        """Returns a cache supporting multiple concurrent non-blocking writes. This cache MUST be used to memoize
        function output."""
        # Dissalow passing directory to the constructor
        kwargs.pop('directory', None)
        cache = diskcache.FanoutCache(directory=self.directory, *args, **kwargs)
        self._caches.append(cache)
        return cache

    def build_deque(self, *args, **kwargs):
        # Dissalow passing directory to the constructor
        kwargs.pop('directory', None)
        cache = diskcache.Deque(directory=self.directory, *args, **kwargs)
        self._caches.append(cache)
        return cache

    def cleanup(self):
        del self._caches[:]
