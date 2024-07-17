import requests
import redis
import time
from functools import wraps

# Initialize Redis client
r = redis.Redis()

def cache_page(expiration=10):
    def decorator(func):
        @wraps(func)
        def wrapper(url, *args, **kwargs):
            cache_key = f"cache:{url}"
            count_key = f"count:{url}"

            # Check if the URL is cached
            cached_page = r.get(cache_key)
            if cached_page:
                r.incr(count_key)
                return cached_page.decode('utf-8')

            # If not cached, fetch the page
            page_content = func(url, *args, **kwargs)
            r.setex(cache_key, expiration, page_content)
            r.incr(count_key)
            return page_content

        return wrapper
    return decorator

@cache_page(expiration=10)
def get_page(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text

# Test the implementation
if __name__ == "__main__":
    test_url = "http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.google.com"
    print(get_page(test_url))  # First access, should fetch from the web
    time.sleep(1)
    print(get_page(test_url))  # Second access, should fetch from the cache
    time.sleep(11)
    print(get_page(test_url))  # After cache expiration, should fetch from the web again
