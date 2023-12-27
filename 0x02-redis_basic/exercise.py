#!/usr/bin/env python3
"""Module for working with Redis."""

import redis
import random
from typing import Union, Optional, Callable
import uuid
from functools import wraps


class Cache:
    """Class for interacting with Redis caching system."""

    def __init__(self) -> None:
        """Initialize Cache object and Redis instance."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @staticmethod
    def count_calls(method: Callable) -> Callable:
        """Decorator that takes a single method Callable
        argument and returns a Callable."""
        key = method.__qualname__

        @wraps(method)
        def wrapper(self, *args, **kwds):
            self._redis.incr(key)
            return method(self, *args, **kwds)

        return wrapper

    @staticmethod
    def call_history(method: Callable) -> Callable:
        """
        Decorator to store the history of inputs and outputs
        for a particular function.
        """
        key = method.__qualname__

        @wraps(method)
        def wrapper(self, *args, **kwds):
            """Stores method's inputs and outputs into Redis lists."""
            self._redis.rpush(f'{key}:inputs', str(args))
            output = method(self, *args, **kwds)
            self._redis.rpush(f'{key}:outputs', str(output))
            return output

        return wrapper

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis and return a unique key for retrieval.

        Args:
            data (Union[str, bytes, int, float]): Data to be stored.

        Returns:
            str: Unique key associated with the stored data.
        """
        r_key = str(uuid.uuid4())
        self._redis.set(r_key, data)
        return r_key

    def get(self, key: str, fn: Callable = None) -> Union[None, str, int]:
        """
        Retrieve data from Redis using the provided key.

        Args:
            key (str): Key associated with the stored data.
            fn (Optional[Callable]): Optional function to transform the retrieved data.

        Returns:
            Union[None, str, int]: Retrieved data or None if key not found.
        """
        value = self._redis.get(key)
        if fn is not None:
            return fn(value)
        return value

    def get_str(self, key: str) -> str:
        """
        Retrieve data from Redis and decode it as a string.

        Args:
            key (str): Key associated with the stored data.

        Returns:
            str: Retrieved data as a string.
        """
        value = self._redis.get(key)
        return value.decode("utf-8")

    def get_int(self, key: str) -> int:
        """
        Retrieve data from Redis and convert it to an integer.

        Args:
            key (str): Key associated with the stored data.

        Returns:
            int: Retrieved data as an integer.
        """
        return int(self._redis.get(key))
