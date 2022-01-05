from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.api import views as uv

app_name = 'users'
router = DefaultRouter()
router.register(r"user", uv.CustomUserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "user/set-realm/<int:realm_id>/",
        uv.RealmSetAPIView.as_view(),
        name="realm-set",
        ),
]