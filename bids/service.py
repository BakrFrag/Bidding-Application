from channels.db import database_sync_to_async
from .models import Bid, BidHistory

class BidModelService:

    @staticmethod
    def _get_bid_sync(bid_id):
        """Internal helper to get the bid object."""
        return Bid.objects.prefetch_related('history').filter(id=bid_id, status="open").first()

    @staticmethod
    def _get_history_sync(bid_obj):
        """Internal helper to get history for an existing object."""
        bids_history = bid_obj.history.all()
        print("bids history:",bids_history, bids_history is not None)
        if bids_history and bids_history is not None:
            return [
                    {"name": h.bidder_name, "price": str(h.price)} 
                    for h in bids_history
            ]
        return {"name": "initial_price", "price": str(bid_obj.initial_price)}


    @staticmethod
    @database_sync_to_async
    def is_bid_exists(bid_id):
        return BidModelService._get_bid_sync(bid_id) is not None

    @staticmethod
    @database_sync_to_async
    def get_bid_history(bid_id):
        bid = BidModelService._get_bid_sync(bid_id)
        if bid is None:
            return None
        return BidModelService._get_history_sync(bid)
    

    @staticmethod
    @database_sync_to_async
    def handle_new_bid(bid_id, name, amount):
        # Reuse the sync helper
        bid_obj = BidModelService._get_bid_sync(bid_id)
        
        if bid_obj is None:
            raise ValueError("Bid not found or closed.")

        latest = bid_obj.history.order_by('-price').first()
        current_max = latest.price if latest else bid_obj.initial_price

        if amount <= current_max:
            raise ValueError(f"Bid must be higher than {current_max}")

        return BidHistory.objects.create(
            bid=bid_obj,
            bidder_name=name,
            price=amount
        )