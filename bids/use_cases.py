
from channels.db import database_sync_to_async
from .models import Bid, BidHistory


class BidModelService:
    """
    include usecases for bid and bid history models.
    """
    @staticmethod
    @database_sync_to_async
    def get_bid_by_id(bid_id):
        """
        Get bid object from db if it exists, else return None.
        """
        return Bid.objects.prefetch_related("history").filter(id=bid_id).first()
        
    
    @staticmethod
    @database_sync_to_async
    def get_bid_history(bid_id):
        """Fetches the latest bid or the initial price if no bids exist."""
        bid = BidModelService.get_bid_by_id(bid_id)
        if bid is not None:
            return {{"name": bid.bidder_name, "price": str(bid.price)} for bid in bid.history.all()}
        return {"name": "Initial Price", "price": str(bid.initial_price)}
    
    @staticmethod
    @database_sync_to_async
    def handle_new_bid(bid_id, name, amount):
        """Validates that the new bid is higher than current, then saves."""
        bid_obj = BidModelService.get_bid_by_id(bid_id)
        latest_bid = bid_obj.history.first()
        current_max = latest_bid.price if latest_bid else bid_obj.initial_price

        if amount <= current_max:
            raise ValueError(f"Your bid of {amount} must be higher than {current_max}")

        return BidHistory.objects.create(
            bid=bid_obj,
            bidder_name=name,
            price=amount
        )