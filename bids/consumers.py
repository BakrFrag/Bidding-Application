import json
import logging
import uuid
from pydantic import ValidationError
from channels.generic.websocket import AsyncWebsocketConsumer
from .schemas import BidSubmissionSchema
from .service import BidModelService

logger = logging.getLogger('bidding')

class BidConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        accept connection to existing bid room based on bid_id from URL.
        """
        self.trace_id = str(uuid.uuid4())[:8]
        self.bid_id = self.scope['url_route']['kwargs']['bid_id']
        self.room_group_name = f'bid_{self.bid_id}'
        logger.debug(f"WebSocket connection attempt. Trace ID: {self.trace_id} for channel: {self.room_group_name}")

        if not await BidModelService.is_bid_exists(self.bid_id):
            logger.warning(f"Bid ID {self.bid_id} does not exist or may be closed. Trace ID: {self.trace_id}")
            await self.close() 
            return 
    
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.send_initial_state()
        logger.debug(f"WebSocket connection accepted. Trace ID: {self.trace_id} for channel: {self.room_group_name}")

    async def send_initial_state(self):
        """
        Send the latest bid data to the user who just connected
        """
        
        current_state = await BidModelService.get_bid_history(self.bid_id)
        await self.send(text_data=json.dumps({
            'type': 'initial_state',
            'data': current_state
        }))
        logger.info(f"Sent initial state to Trace ID: {self.trace_id} for channel: {self.room_group_name}")
        

    async def disconnect(self, close_code):
        """
        Leave the group when the user closes the tab/internet drops
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.debug(f"WebSocket disconnected. Trace ID: {self.trace_id} for channel: {self.room_group_name} with code {close_code}")

    async def receive(self, text_data):
        """
        Triggered when a user sends a bid via WebSocket.
        new bid amount > current highest bid.
        """
        try:
            data = json.loads(text_data)
            data_validated = BidSubmissionSchema(**data)
            logger.info(f"Received new bid from {data_validated.name} for amount {data_validated.price}. Trace ID  : {self.trace_id}")
            new_bid = await BidModelService.handle_new_bid(
                bid_id = self.bid_id,
                name = data_validated.name,
                amount = data_validated.price
            )
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'bid_update', 
                    'price': str(new_bid.price),
                    'bidder': new_bid.bidder_name
                }
            )
            logger.info(f"Broadcasted new bid of {new_bid.price} by {new_bid.bidder_name}. Trace ID: {self.trace_id}")

        except ValidationError as e:
            logger.error(f"Validation error for bid submission. Trace ID: {self.trace_id}. Errors: {e.errors()}")
            await self.send(text_data=json.dumps({'type': 'error', 'message': e.errors()}))
        except ValueError as e:
            logger.error(f"Value error for bid submission. Trace ID: {self.trace_id}. Error: {str(e)}")
            await self.send(text_data=json.dumps({'type': 'error', 'message': str(e)}))
        except Exception as e:
            logger.exception(f"Unexpected error processing bid. Trace ID: {self.trace_id} as {str(e)}")
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Internal Server Error'}))

    async def bid_update(self, event):
        """
        This handler sends the broadcast message to the actual WebSocket.
        """
        logger.debug(f"Sending bid update to Trace ID: {self.trace_id} with data: {event}")
        await self.send(text_data=json.dumps({
            'type': 'new_bid',
            'price': event['price'],
            'bidder': event['bidder']
        }))

   