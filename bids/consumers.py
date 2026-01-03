import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from decimal import Decimal
from .models import Bid, BidHistory

class BidConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract the bid ID from the URL (e.g., /ws/bid/5/)
        self.bid_id = self.scope['url_route']['kwargs']['bid_id']
        self.room_group_name = f'bid_{self.bid_id}'

        # Join the group (the 'Conference Call')
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Catch up: Send the latest bid data to the user who just connected
        current_state = await self.get_current_bid_state()
        await self.send(text_data=json.dumps({
            'type': 'initial_state',
            'data': current_state
        }))

    async def disconnect(self, close_code):
        # Leave the group when the user closes the tab/internet drops
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Triggered when a user (like Bakr) sends a bid via WebSocket.
        """
        try:
            data = json.loads(text_data)
            bidder_name = data.get('name')
            bid_amount = Decimal(str(data.get('price')))

            # 1. Validate and save to Database using the sync-to-async bridge
            new_bid = await self.handle_new_bid(bidder_name, bid_amount)

            # 2. Broadcast the successful bid to EVERYONE in the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'bid_update', # Calls the bid_update method below
                    'price': str(new_bid.price),
                    'bidder': new_bid.bidder_name
                }
            )

        except ValueError as e:
            # Send specific validation error (e.g., "Bid too low") only to the sender
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
        except Exception as e:
            # General error handling
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'An unexpected error occurred.'
            }))

    async def bid_update(self, event):
        """
        This handler sends the broadcast message to the actual WebSocket.
        """
        await self.send(text_data=json.dumps({
            'type': 'new_bid',
            'price': event['price'],
            'bidder': event['bidder']
        }))

    # --- Database Operations (Wrapped for Async) ---

    @database_sync_to_async
    def get_current_bid_state(self):
        """Fetches the latest bid or the initial price if no bids exist."""
        bid_obj = Bid.objects.get(id=self.bid_id)
        latest_bid = BidHistory.objects.filter(bid=bid_obj).order_by('-price').first()
        
        if latest_bid:
            return {'price': str(latest_bid.price), 'bidder': latest_bid.bidder_name}
        return {'price': str(bid_obj.initial_price), 'bidder': 'No bids yet'}

    @database_sync_to_async
    def handle_new_bid(self, name, amount):
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