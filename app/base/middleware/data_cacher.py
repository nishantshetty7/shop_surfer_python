from django.conf import settings
from rest_framework.response import Response
from django.core.cache import cache
import json
from functools import wraps

class DataCacher:
    def __init__(self):
        pass

    def __call__(self, fn):

        @wraps(fn)
        def wrapper(request, *args, **kwargs):
            print("INIT_CACHE")
            print("VIEW ARGS: ", args)
            print("VIEW KWARGS: ", kwargs)
            self.args = args
            self.kwargs = kwargs
            self.generate_cache_key(request)
            cached_data = cache.get(self.cache_key)
            if cached_data and self.cache_mode == "rw":
                print("CACHE READ")
                # If cached data exists, return it directly
                return Response(json.loads(cached_data))
            response = fn(request, *args, **kwargs)
            if response.status_code == 200:
                # writes to cache if cache_mode=w(write) or if cache_data does not exist
                print("CACHE WRITE")
                cache.set(self.cache_key, json.dumps(response.data), timeout=settings.CACHE_TTL)
            return response
        return wrapper

    def generate_cache_key(self, request):
        path = request.path
        if "product/" in path:
            slug = self.kwargs.get("slug", "")
            self.cache_key = f"product:{slug}"
            self.cache_mode = "rw"
        elif "cart/" in path:
            user_id = request.user_id
            self.cache_key = f"cart:{user_id}"
            if path == "/data/cart/":
                self.cache_mode = "rw"
            else:
                self.cache_mode = "w"
        elif "address/" in path:
            user_id = request.user_id
            self.cache_key = f"address:{user_id}"
            if path == "/data/address/":
                self.cache_mode = "rw"
            else:
                self.cache_mode = "w"
        print("CACHE_KEY: ", self.cache_key)
        print("CACHE_MODE: ", self.cache_mode)