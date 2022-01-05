from django.urls import include, path
from rest_framework.routers import DefaultRouter

from items.api import views as iv

app_name = 'items'
router = DefaultRouter()
router.register(r"items", iv.ItemViewSet, basename="items")
router.register(r"itemDetails", iv.ItemDetailsViewSet, basename="itemDetails")
router.register(r"auctions", iv.AuctionViewSet)
router.register(r"user-items", iv.UserItemsViewSet, basename="user-items")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "items/<int:item_id>/follow/",
        iv.ItemFollowAPIView.as_view(),
        name="item-follow",
        ),
]