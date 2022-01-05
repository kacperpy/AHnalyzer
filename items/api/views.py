from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import datetime

from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from items.models import Item, Auction
from items.api.serializers import ItemSerializer, ItemDetailsSerializer, AuctionSerializer

from items.api.permissions import IsAdminUserOrReadOnly


DEFAULT_REALM = 4455


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    lookup_field = "item_id"

    # @method_decorator(cache_page(60*5))
    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):


        #1ST DATA UPDATE @ 00:00AM
        #2ND DATA UPDATE @ 12:00PM


        now = datetime.now()

        update_1_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        update_2_time = now.replace(hour=12, minute=0, second=0, microsecond=0)

        category_name = self.request.query_params.get("category", None)
        option = self.request.query_params.get("option", None)
        item_name = self.request.query_params.get("name", None)
        USER_REALM_ID = self.request.user.realm_id if self.request.user.is_authenticated else DEFAULT_REALM
        
        if category_name is None and option is None and item_name is None:
            queryset = Item.objects.all()
        elif item_name is not None:
            queryset = Item.objects.filter(name__contains=item_name)
        elif category_name is not None:
            queryset = Item.objects.prefetch_related('auctions').filter(
                category=category_name,
                auctions__realm_id=USER_REALM_ID).order_by("item_id")
        elif option is not None:
            if int(option) == 1:
                queryset = Item.objects.prefetch_related('auctions').filter(
                    auctions__realm_id=USER_REALM_ID
                    ).exclude(auctions__isnull=True).order_by("item_id")
            elif int(option) == 2:
                if now < update_2_time:
                    queryset = Item.objects.prefetch_related('auctions').filter(
                        auctions__realm_id=USER_REALM_ID,
                        auctions__created_at__gt=update_1_time
                        ).order_by('item_id')
                else:
                    queryset = Item.objects.prefetch_related('auctions').filter(
                        auctions__realm_id=USER_REALM_ID,
                        auctions__created_at__gt=update_2_time
                        ).order_by('item_id')

        return queryset.distinct()

class ItemDetailsViewSet(viewsets.ModelViewSet):
    serializer_class = ItemDetailsSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    lookup_field = "item_id"
    queryset = Item.objects.all()

class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.all().order_by("-updated_at")
    serializer_class = AuctionSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "auction_id"

    def perform_create(self, serializer):
        item = get_object_or_404(Item, item_id=self.request.data["item_id"])
        serializer.save(auctioned_item=item)

class UserItemsViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Item.objects.filter(followed_by__in=[self.request.user])

class ItemFollowAPIView(APIView):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):
        item = get_object_or_404(Item, item_id=item_id)
        item.followed_by.add(request.user)
        item.save()
        return Response(f"item {item_id} added to followed list", status=status.HTTP_200_OK)

    def delete(self, request, item_id):
        item = get_object_or_404(Item, item_id=item_id)
        item.followed_by.remove(request.user)
        item.save()
        return Response(f"item {item_id} removed from followed list", status=status.HTTP_200_OK)