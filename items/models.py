from django.db import models
from core.models import TimeStampedModel
from django.conf import settings


class Item(models.Model):
    item_id = models.IntegerField(
        db_index=True,
        primary_key=True,
        unique=True)
    name = models.CharField(max_length=240)
    category = models.CharField(max_length=100)
    media = models.URLField()
    followed_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="followed_items")

    def __str__(self):
        return self.name


class Auction(TimeStampedModel):
    auction_id = models.BigIntegerField(db_index=True)
    price = models.IntegerField()
    quantity = models.IntegerField()
    item_id = models.IntegerField()
    auctioned_item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="auctions",
        blank=True,
        null=True,
        db_index=True)
    realm_id = models.IntegerField()

    def __str__(self):
        return str(self.auction_id)