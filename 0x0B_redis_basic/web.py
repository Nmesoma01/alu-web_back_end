#!/usr/bin/env python3
'''A module with tools for request caching and tracking.
'''
import redis
import requests
from functools import wraps
from typing import Callable


redis_store = redis.Redis()
'''The module-level Redis instance.
'''


def data_cacher(method: Callable) -> Callable:
    '''Caches the output of fetched data and tracks the count of requests.
    '''
    @wraps(method)
    def invoker(url) -> str:
        '''The wrapper function for caching the output.
        '''
        redis_store.incr(f'count:{url}')  # Increment the count for the URL
        result = redis_store.get(f'result:{url}')
        if result:
            return result.decode('utf-8')

        # Fetch data from the URL if not found in the cache
        try:
            result = method(url)
            redis_store.set(f'result:{url}', result, ex=10)  # Set cache with expiry of 10 seconds
            return result
        except Exception as e:
            # Log or handle the exception accordingly
            print(f"Error fetching data from {url}: {e}")
            return ""

    return invoker


@data_cacher
def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response,
    and tracking the request.
    '''
    return requests.get(url).text
