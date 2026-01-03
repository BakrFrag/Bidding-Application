
from channels.db import database_sync_to_async
from .models import Bid, BidHistory

@database_sync_to_async
def bid_exists(bid_id):
    """Checks if the auction item exists in the database."""
    return Bid.objects.filter(id=bid_id).exists()

@database_sync_to_async
def get_current_bid_state(self):
    """Fetches the latest bid or the initial price if no bids exist."""
    bid_obj = Bid.objects.get(id=self.bid_id)
    latest_bid = BidHistory.objects.filter(bid=bid_obj).order_by('-price').first()
    
    if latest_bid:
        return {'price': str(latest_bid.price), 'bidder': latest_bid.bidder_name}
    return {'price': str(bid_obj.initial_price), 'bidder': 'No bids yet'}

@database_sync_to_async
def handle_new_bid( name, amount):
    """Validates that the new bid is higher than current, then saves."""
    bid_obj = Bid.objects.get(id=self.bid_id)
    
    # Lock the row for update to prevent two people bidding the same price at the exact same millisecond
    latest_bid = BidHistory.objects.filter(bid=bid_obj).order_by('-price').first()
    current_max = latest_bid.price if latest_bid else bid_obj.initial_price

    if amount <= current_max:
        raise ValueError(f"Your bid of {amount} must be higher than {current_max}")

    return BidHistory.objects.create(
        bid=bid_obj,
        bidder_name=name,
        price=amount
    )