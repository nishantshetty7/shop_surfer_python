# shopsurfer_cacher.py

from django.core.cache import cache
from django.conf import settings
from django.shortcuts import HttpResponse
import json

class CacheMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response
        self.init_cache()

    def init_cache(self):
        print("INIT_CACHE")
        self.is_cachable = False
        self.cache_key = None
        self.cache_mode = None
        self.view_args = None
        self.view_kwargs = None
        self.cached_data = None

    def __call__(self, request):
        response = self.get_response(request)

        if self.is_cachable and response.status_code == 200:
            response = self.process_response(request, response)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        print("PROCESS_VIEW")
        self.init_cache()
        # print(request.user)
        self.view_args = view_args
        self.view_kwargs = view_kwargs
        print("ARGS: ",view_args)
        print("KWARGS: ",view_kwargs)
        self.check_cachable(request)
        if self.is_cachable:
            return self.process_request(request)

    def process_request(self, request):
        print("PROCESS_REQUEST")
        # Check cache for cached data
        self.cached_data = cache.get(self.cache_key)
        if self.cached_data:
            print("READ FROM CACHE")
            # If cached data exists, return it directly
            return HttpResponse(self.cached_data)

        # Proceed to the next middleware in the chain
        return None

    def process_response(self, request, response):
        print("PROCESS_RESPONSE")
        # Check if the requested endpoint is one that requires caching
        # Write response data to cache
        if self.cache_mode == "w" or not self.cached_data:
            print("DATA CACHED")
            cache.set(self.cache_key, json.dumps(response.data), timeout=settings.CACHE_TTL)  # Cache indefinitely for write-based endpoints

        return response

    def check_cachable(self, request):
        path = request.path
        print("check_cachable: ", path)
        if "product/" in path:
            slug = self.view_kwargs.get("slug", "")
            self.cache_key = f"product:{slug}"
            self.cache_mode = "rw"
        elif "cart/" in path:
            print(request.user.id)
            self.cache_key = f"cart:{request.user.id}"
            if path != "/data/cart/":
                self.cache_mode = "w"
            else:
                self.cache_mode = "rw"
        elif "address/" in path:
            self.cache_key = "address" 
            if path != "/data/address/":
                self.cache_mode = "w"
            else:
                self.cache_mode = "rw"
        # List of endpoints to cache
        self.is_cachable = True if self.cache_key else False

    def generate_cache_key(self, request):
        # Generate cache key based on endpoint and query parameters
        # For example, you could concatenate the endpoint path with sorted query parameters
        cache_key = ""
        if "product/" in request.path:
            slug = self.view_kwargs.get("slug", "")
            cache_key = f"product:{slug}"
        if "cart/" in request.path:
            print(request.user)
            user = request.user
            cache_key = f"cart:{user.id}"
        elif "address/" in request.path:
            print(request.user)
            user = request.user
            cache_key = f"address:{user.id}"

        print("CACHE_KEY: ", cache_key)
        return cache_key
