from celery import shared_task

from datetime import datetime

from items.models import Auction, Item

from .wow_api.functions import generate_access_token, get_auction_dataframes


@shared_task(bind=True)
def fill_data_auctions(self):

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

@shared_task(bind=True)
def test(self):
    print('------------------------')
    return('test done')