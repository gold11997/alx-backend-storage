#!/usr/bin/env python3
""" 0. Writing strings to Redis"""
import redis
import random
from typing import Union, Optional, Callable
import uuid
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Decorator that takes a single method Callable
    argument and returns a Callable."""
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwds):
        self._redis.incr(key)
        return method(self, *args, **kwds)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    decorator to store the history of inputs and outputs
    for a particular function
    """
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwds):
        """stores method's inputs and outputs into redis lists"""
        self._redis.rpush(f'{key}:inputs', str(args))
        output = method(self, *args, **kwds)
        self._redis.rpush(f'{key}:outputs', str(output))
        return output
    return wrapper


def replay(method: Callable) -> None:
    """replay function to display the history of calls of
    a particular function. Use keys generated in previous
    tasks to generate the following output:"""
    r_instance = method.__self__._redis
    key = method.__qualname__
    n_calls = r_instance.get(key).decode("utf-8")
    print(f'{key} was called {n_calls} times:')
    fn_inputs = r_instance.lrange(f'{key}:inputs', 0, -1)
    fn_outputs = r_instance.lrange(f'{key}:outputs', 0, -1)
    fn_inout = list(zip(fn_inputs, fn_outputs))
    for input, output in fn_inout:
        input = input.decode('utf-8')
        output = output.decode('utf-8')
        print(f"{key}(*{input}) -> {output}")


class Cache():
    """ initializes Redis"""
    def __init__(self) -> None:
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        r_key = str(uuid.uuid4())
        self._redis.set(r_key, data)
        return r_key

    def get(self, key: str, fn: Callable = None):
        """ take a key string argument and an
        optional Callable argument named fn"""
        value = self._redis.get(key)
        if fn is not None:
            return fn(value)
        return value

    def get_str(self, key: str) -> str:
        """parametrize Cache.get to str"""
        value = self._redis.get(key)
        return value.decode("utf-8")

    def get_int(self, key: str) -> int:
        """parametrize Cache.get to int"""
        return int(key)
