import json
from pydantic import ValidationError
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Bid, BidHistory
from .schemas import BidSubmissionSchema

class BidConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        accept connection to existing bid room based on bid_id from URL.
        """
        self.bid_id = self.scope['url_route']['kwargs']['bid_id']
        self.room_group_name = f'bid_{self.bid_id}'

        if not await self.bid_exists(self.bid_id):
            await self.close() # Reject the connection
            return 
    
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.send_initial_state()

    async def send_initial_state(self):
        """
        Send the latest bid data to the user who just connected
        """
        current_state = await self.get_current_bid_state()
        await self.send(text_data=json.dumps({
            'type': 'initial_state',
            'data': current_state
        }))


    async def disconnect(self, close_code):
        """
        Leave the group when the user closes the tab/internet drops
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Triggered when a user sends a bid via WebSocket.
        new bid amount > current highest bid.
        """
        try:
            data = json.loads(text_data)
            data_validated = BidSubmissionSchema(**data)
            new_bid = await self.handle_new_bid(
                data_validated.name,
                data_validated.price
            )
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'bid_update', # Calls the bid_update method below
                    'price': str(new_bid.price),
                    'bidder': new_bid.bidder_name
                }
            )

        except ValidationError as e:
            await self.send(text_data=json.dumps({'type': 'error', 'message': e.errors()}))
        except ValueError as e:
            await self.send(text_data=json.dumps({'type': 'error', 'message': str(e)}))
        except Exception:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Internal Server Error'}))

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
   