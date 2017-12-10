import tempfile
import os
import logging
import time

import diskcache

# Use this method on a FanoutCache object to memoize function output
memoized_result = diskcache.fanout.memoize

log = logging.getLogger(__name__)


# See http://www.grantjenks.com/docs/diskcache/api.html
# for examples on how to interface with the cache objects!

class CacheManager:
    def __init__(self, storage_path=None):
        if storage_path:
            if os.path.isdir(storage_path):
                raise FileNotFoundError('The provided path is not a valid directory!')
            self.tempdir = os.path.abspath(storage_path)
        else:
            self.tempdir = os.path.join(tempfile.gettempdir(), 'pingu-bot')

        self._global_cache = self._build_global_cache()
        self._arenas = {}
        log.info(f'Cache folder: {self.tempdir}')

    def _build_global_cache(self):
        # GlobalCache is actually an arena in itself.
        # We persist the arena path, because global data is intended to survive rebooting the bot!
        global_dir = os.path.join(self.tempdir, 'global')
        return GlobalCache(global_dir)

    def _build_tmp_path(self):
        return os.path.join(self.tempdir, str(time.time()))

    @property
    def global_cache(self):
        return self._global_cache

    def create_arena(self, arena_name):
        """
        Allocates a new cache folder where data for a specific scenario can be stored.
        This method returns None if the name is already in use!
        """
        new_arena = None
        if arena_name not in self._arenas:
            arena_path = os.path.join(self._build_tmp_path(), arena_name)
            self._arenas[arena_name] = CacheArena(arena_path, arena_name)
        return new_arena

    def remove_arena(self, arena_name):
        return self._arenas.pop(arena_name, None) is not None

    def cleanup(self):
        del self._global_cache
        self._arenas.clear()


class GlobalCache(diskcache.Index):
    """Represents a disk persistent key-value store for global usage."""

    def __init__(self, directory, *args, **kwargs):
        super().__init__(directory, *args, **kwargs)


class CacheArena:
    """Manages a specific cache directory. All cache objects built from this arena work on THE SAME data!
    Build multiple arenas for each different purpose!
    """

    def __init__(self, directory, name):
        self.directory = os.path.join(directory, name)
        self.name = name
        self._caches = []

    def build_simple_cache(self, directory=None, *args, **kwargs):
        """Returns a simple key-value cache with automatic eviction enabled.
        When multiple processes cache over the same directory IPC can be achieved!
        """
        if not directory:
            directory = self.directory
        cache = diskcache.Cache(directory=directory, *args, **kwargs)
        self._caches.append(cache)
        return cache

    def build_index(self, *args, **kwargs):
        """Returns a persistent key-value cache without automatic eviction.
        An index offers ordered dictionary (insertion order is preserved) functionality.
        Usage of this type of cache is thread safe."""
        # Dissalow passing directory to the constructor
        kwargs.pop('directory', None)
        cache = diskcache.Index(self.directory, **kwargs) # Disallow data insertion on construction (*args)
        self._caches.append(cache)
        return cache

    def build_fanout(self, *args, **kwargs):
        """Returns a non-persistant cache supporting multiple concurrent non-blocking writes.
        This cache MUST be used to memoize function output.
        """
        # Dissalow passing directory to the constructor
        kwargs.pop('directory', None)
        cache = diskcache.FanoutCache(directory=self.directory, **kwargs)
        self._caches.append(cache)
        return cache

    def build_deque(self, *args, **kwargs):
        """Returns a persistent cache supporting FIFO queue operations. Both ends can be manipulated.
        This cache can be used to build a threadsafe command queue."""
        # Dissalow passing directory to the constructor
        kwargs.pop('directory', None)
        cache = diskcache.Deque(directory=self.directory, **kwargs)
        self._caches.append(cache)
        return cache

    def cleanup(self):
        del self._caches[:]
