from asyncio import iscoroutinefunction
from urllib import response
from django.utils.deprecation import MiddlewareMixin
from django.utils.cache import patch_cache_control
from asgiref.sync import iscoroutinefunction, markcoroutinefunction
 
class MediaCacheControlMiddleware:
    async_capable = True
    sync_capable = False

    def __init__(self, get_response):
        self.get_response = get_response
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    async def __call__(self, request):
        response = await self.get_response(request)
        if request.path.startswith("/project/"):
            patch_cache_control(response, public=True, max_age=31536000, immutable=True)
            print("MediaCacheControlMiddleware applied")
        return response
