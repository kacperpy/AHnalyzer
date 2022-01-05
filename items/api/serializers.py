from datetime import timedelta
from django.utils.timezone import datetime
from django.utils import timezone
from django.db.models import Avg, Min, Max, Sum
from rest_framework import serializers
from items.models import Item, Auction

import logging


DEFAULT_REALM = 4455


class ItemSerializer(serializers.ModelSerializer):
    available = serializers.SerializerMethodField()
    cur_min_price = serializers.SerializerMethodField()
    median_value_3day = serializers.SerializerMethodField()
    mean_value_3day = serializers.SerializerMethodField()
    last_auctioned = serializers.SerializerMethodField()
    percent_change_24h = serializers.SerializerMethodField()
    is_followed_by_cur_user = serializers.SerializerMethodField()

    class Meta:
        model = Item
        exclude = ["followed_by"]

    # Current minimal price on the market
    def get_cur_min_price(self, instance):
        now = datetime.now()
        UPDATE_1_TIME = now.replace(hour=0, minute=0, second=0, microsecond=0)
        UPDATE_2_TIME = now.replace(hour=12, minute=0, second=0, microsecond=0)

        USER_REALM_ID = self.context['request'].user.realm_id if self.context['request'].user.is_authenticated else DEFAULT_REALM

        if now < UPDATE_2_TIME:
            results = instance.auctions.filter(
                created_at__gt=UPDATE_1_TIME,
                realm_id=USER_REALM_ID)
        else:
            results = instance.auctions.filter(
                created_at__gt=UPDATE_2_TIME,
                realm_id=USER_REALM_ID)

        try:
            return '{:,}'.format(results.aggregate(Min('price'))["price__min"]).replace(',', ' ')
        except:
            return None
    
    # Median value of price from last 3 days
    def get_median_value_3day(self, instance):
        USER_REALM_ID = self.context['request'].user.realm_id if self.context['request'].user.is_authenticated else DEFAULT_REALM
        today = datetime.today()
        start_date = today - timedelta(days=3)
        queryset = instance.auctions.filter(created_at__range=[start_date, today], realm_id=USER_REALM_ID)
        count = queryset.count()
        values = queryset.values_list("price", flat=True).order_by("price")
        result = 0
        
        try:
            if count % 2 == 1:
                result = values[int(round(count/2))]
            else:
                result = sum(values[count/2-1:count/2+1])/2.0
        except Exception as e:
            logging.error(f"ERROR IN: serializers.get_median_value_3day: \n{e}")

        return '{:,}'.format(result).replace(',', ' ')

    # Mean value of price from last 3 days
    def get_mean_value_3day(self, instance):
        USER_REALM_ID = self.context['request'].user.realm_id if self.context['request'].user.is_authenticated else DEFAULT_REALM
        today = datetime.today()
        start_date = today - timedelta(days=3)
        results = instance.auctions.filter(created_at__range=[start_date, today], realm_id=USER_REALM_ID)
        result = 0
        try:
            result = round(results.aggregate(Avg('price'))["price__avg"],0)
        except:
            pass
        return '{:,}'.format(result).replace(',', ' ')

    # Currently available quantity on the market
    def get_available(self, instance):
        now = datetime.now()
        UPDATE_1_TIME = now.replace(hour=0, minute=0, second=0, microsecond=0)
        UPDATE_2_TIME = now.replace(hour=12, minute=0, second=0, microsecond=0)

        USER_REALM_ID = self.context['request'].user.realm_id if self.context['request'].user.is_authenticated else DEFAULT_REALM

        if now < UPDATE_2_TIME:
            queryset = instance.auctions.filter(
                created_at__gt=UPDATE_1_TIME,
                realm_id=USER_REALM_ID)
        else:
            queryset = instance.auctions.filter(
                created_at__gt=UPDATE_2_TIME,
                realm_id=USER_REALM_ID)

        results = queryset.aggregate(Sum('quantity'))["quantity__sum"]
        return results if not results == None else 0

    def get_last_auctioned(self, instance):
        USER_REALM_ID = self.context['request'].user.realm_id if self.context['request'].user.is_authenticated else DEFAULT_REALM
        queryset = instance.auctions.filter(
            realm_id=USER_REALM_ID
        ).aggregate(Max('created_at'))['created_at__max']
        if queryset is not None:
            return timezone.localtime(queryset).strftime('%Y-%m-%d %H:%M')
        return None
    
    def get_percent_change_24h(self, instance):
        USER_REALM_ID = self.context['request'].user.realm_id if self.context['request'].user.is_authenticated else DEFAULT_REALM
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        min_today = 0
        min_yesterday = 0
        change = 0

        query_today = instance.auctions.filter(
            created_at__year=today.year,
            created_at__month=today.month,
            created_at__day=today.day,
            realm_id=USER_REALM_ID)

        query_yesterday = instance.auctions.filter(
            created_at__year=yesterday.year,
            created_at__month=yesterday.month,
            created_at__day=yesterday.day,
            realm_id=USER_REALM_ID)

        try:
            min_today = float(query_today.aggregate(Min('price'))["price__min"])
            min_yesterday = float(query_yesterday.aggregate(Min('price'))["price__min"])

            if not min_today == min_yesterday:
                change = round(((abs(min_today - min_yesterday) / min_yesterday) * 100.0), 2)
        except:
            return "No Data"

        if float(min_today) > float(min_yesterday) and change != 0:
            return f"▴{change}%"
        elif float(min_today) < float(min_yesterday) and change != 0:
            return f"▾{change}%"
        else:
            return "0.0%"

    def get_is_followed_by_cur_user(self, instance):
        request = self.context.get("request")
        return instance.followed_by.filter(pk=request.user.pk).exists()

class ItemDetailsSerializer(ItemSerializer):
    median_value_7day = serializers.SerializerMethodField()
    mean_value_7day = serializers.SerializerMethodField()
    last_7_days_min = serializers.SerializerMethodField()
    last_7_days_available = serializers.SerializerMethodField()
    percent_change_72h = serializers.SerializerMethodField()

    def get_median_value_7day(self, instance):
        USER_REALM_ID = self.context['request'].user.realm_id if self.context['request'].user.is_authenticated else DEFAULT_REALM
        today = datetime.today()
        start_date = today - timedelta(days=7)
        queryset = instance.auctions.filter(created_at__range=[start_date, today], realm_id=USER_REALM_ID)
        count = queryset.count()
        values = queryset.values_list("price", flat=True).order_by("price")
        result = 0
        
        try:
            if count % 2 == 1:
                result = values[int(round(count/2))]
            else:
                result = sum(values[count/2-1:count/2+1])/2.0
        except Exception as e:
            logging.error(f"ERROR IN: serializers.get_median_value_3day: \n{e}")

        return '{:,}'.format(result).replace(',', ' ')
    
    def get_mean_value_7day(self, instance):
        USER_REALM_ID = self.context['request'].user.realm_id if self.context['request'].user.is_authenticated else DEFAULT_REALM
        today = datetime.today()
        start_date = today - timedelta(days=7)
        results = instance.auctions.filter(created_at__range=[start_date, today], realm_id=USER_REALM_ID)
        result = 0
        try:
            result = round(results.aggregate(Avg('price'))["price__avg"],0)
        except:
            pass
        return '{:,}'.format(result).replace(',', ' ')

    # Minimal prices from last 7 days
    def get_last_7_days_min(self, instance):
        USER_REALM_ID = self.context['request'].user.realm_id if self.context['request'].user.is_authenticated else DEFAULT_REALM
        result_list = []
        cur_day = datetime.today()
        for i in range(1,8):
            queryset = instance.auctions.filter(
                created_at__year=cur_day.year,
                created_at__month=cur_day.month,
                created_at__day=cur_day.day,
                realm_id=USER_REALM_ID)
            result = queryset.aggregate(Min('price'))["price__min"]
            result_list.append(result)
            cur_day = datetime.today() - timedelta(days=i)
        return result_list
    
    def get_last_7_days_available(self, instance):
        USER_REALM_ID = self.context['request'].user.realm_id if self.context['request'].user.is_authenticated else DEFAULT_REALM
        result_list = []
        cur_day = datetime.today()
        for i in range(1,8):
            queryset = instance.auctions.filter(
                created_at__year=cur_day.year,
                created_at__month=cur_day.month,
                created_at__day=cur_day.day,
                realm_id=USER_REALM_ID)
            result = queryset.aggregate(Sum('quantity'))["quantity__sum"]
            result_list.append(result)
            cur_day = datetime.today() - timedelta(days=i)
        return result_list

    def get_percent_change_72h(self, instance):
        USER_REALM_ID = self.context['request'].user.realm_id if self.context['request'].user.is_authenticated else DEFAULT_REALM
        today = datetime.today()
        days_ago_3 = today - timedelta(days=3)
        min_today = 0
        min_days_ago_3 = 0
        change = 0

        query_today = instance.auctions.filter(
            created_at__year=today.year,
            created_at__month=today.month,
            created_at__day=today.day,
            realm_id=USER_REALM_ID)

        query_days_ago_3 = instance.auctions.filter(
            created_at__year=days_ago_3.year,
            created_at__month=days_ago_3.month,
            created_at__day=days_ago_3.day,
            realm_id=USER_REALM_ID)

        try:
            min_today = float(query_today.aggregate(Min('price'))["price__min"])
            min_days_ago_3 = float(query_days_ago_3.aggregate(Min('price'))["price__min"])

            if not min_today == min_days_ago_3:
                change = round(((abs(min_today - min_days_ago_3) / min_days_ago_3) * 100.0), 2)
        except:
            return "No Data"

        if float(min_today) > float(min_days_ago_3) and change != 0:
            return f"▴{change}%"
        elif float(min_today) < float(min_days_ago_3) and change != 0:
            return f"▾{change}%"
        else:
            return "0.0%"

class AuctionSerializer(serializers.ModelSerializer):
    auctioned_item = serializers.StringRelatedField()

    class Meta:
        model = Auction
        exclude = []