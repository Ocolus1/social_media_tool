# urls.py

from django.contrib import admin
from django.urls import path, include
from ninja import NinjaAPI
from ninja.security import HttpBearer
from ninja_jwt.authentication import JWTAuth
from users.api import router as users_router
from posts.api import router as posts_router
from ninja_jwt.routers.obtain import obtain_pair_router
from ninja_jwt.routers.verify import verify_router


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        return JWTAuth().authenticate(request, token)


api = NinjaAPI(auth=AuthBearer())

api.add_router("/login", tags=["Auth"], router=obtain_pair_router)
api.add_router("/token", tags=["Auth"], router=verify_router)
api.add_router("/users/", tags=["Users"], router=users_router)
api.add_router("/posts/", tags=["Posts"], router=posts_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("social_django.urls", namespace="social")),
    path("api/", api.urls),
]
