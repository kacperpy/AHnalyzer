import requests
from requests.structures import CaseInsensitiveDict
import json
import pandas as pd
from urllib.request import urlopen
from datetime import datetime

from items.models import Auction, Item


def generate_access_token():

    url = "https://us.battle.net/oauth/token"

    headers = CaseInsensitiveDict()
    headers["User-Agent"] = "Mozilla/5.0"
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    headers["Authorization"] = "Basic Zjg0OWI5ZTEwYWZkNDhiODhkNGY3ZGY4MTk5YWU2ODI6YW5GdFJnbXZZOTRSMzZ3TndHcmdjUGlFT0FCQnBPNHQ="

    data = "grant_type=client_credentials"

    response = requests.post(url, headers=headers, data=data)

    access_token = json.loads(response.content)["access_token"]
    return access_token

def get_auction_dataframes(realms, access_token):

    dataframes = []

    for realm in realms:

        url = f"https://eu.api.blizzard.com/data/wow/connected-realm/{realm}/auctions/2?namespace=dynamic-classic-eu&locale=en_US&access_token={access_token}"
        
        response = urlopen(url, timeout=10)

        data = json.loads(response.read())

        df = pd.json_normalize(data, record_path=["auctions"])
        df = df.drop(columns=['bid', 'time_left', 'item.rand', 'item.seed'])
        df = df.drop_duplicates(subset=['id']).set_index("id")
        df['realm_id'] = realm

        dataframes.append(df)

    return dataframes

def clear_auctions():
        batch_size = 1000
        while Auction.objects.all().count():
            try:
                Auction.objects.filter(pk__in=Auction.objects.all().values_list('pk')[:batch_size]).delete()
                print("deleted 1000 records")
            except Exception as e:
                print(f"hereeeeee {e}")

def fill_data_auctions():

    start = datetime.now()

    realms = [4441, 4455]

    access_token = generate_access_token()
    dataframes = get_auction_dataframes(realms, access_token)

    for dataframe in dataframes:
        cur_auctions = []
        for index, row in dataframe.iterrows():
            cur_auctions.append(
                Auction(
                    auction_id=index,
                    price=row['buyout'],
                    quantity=row['quantity'],
                    item_id=row['item.id'],
                    auctioned_item=Item.objects.get(item_id=row['item.id']) if Item.objects.filter(item_id=row['item.id']).exists() else None,
                    realm_id = row['realm_id']
                )
            )
        cur_auctions_ids = list(set([auction.auction_id for auction in cur_auctions]))

        CUR_BATCH_START = 0
        BATCH_SIZE = 1000

        while len(cur_auctions_ids[CUR_BATCH_START:CUR_BATCH_START+BATCH_SIZE]) != 0:
            cur_auctions_ids_batch = cur_auctions_ids[CUR_BATCH_START:CUR_BATCH_START+BATCH_SIZE]
            Auction.objects.filter(auction_id__in=cur_auctions_ids_batch).delete()
            CUR_BATCH_START = CUR_BATCH_START + BATCH_SIZE

        Auction.objects.bulk_create(objs=cur_auctions)

    total_duration = (datetime.now() - start).total_seconds()
    return(f"finished filling data in: {total_duration}s")