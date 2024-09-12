import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import AuthenticationFailed
from .authentication import validate_jwt_token, get_user, user_has_access
from .board_utils import get_board_lists

class BoardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Initialize room_group_name with a default value
        self.room_group_name = None

        # Get the JWT token from the cookies
        token = self.scope['cookies'].get('accessToken')

        if not token:
            await self.close()
            return

        # Validate the JWT token and authenticate the user
        try:
            decoded_data = validate_jwt_token(token)
            user = await get_user(decoded_data['user_id'])
            if user == AnonymousUser():
                await self.close()
                return
        except AuthenticationFailed:
            # If authentication fails, close the connection
            await self.close()
            return

        self.scope['user'] = user

        # Get the board ID from the URL route
        self.board_id = self.scope['url_route']['kwargs']['board_id']

        # Check if the user has access to the board
        if not await user_has_access(self.board_id, user):
            await self.close()
            return

        self.room_group_name = f'board_{self.board_id}'

        # Join the board's room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

        # Send lists to the user
        lists = await get_board_lists(self.board_id)
        await self.send(text_data=json.dumps({
            'type': 'initial_lists',
            'lists': lists
        }))

    async def disconnect(self, close_code):
        if self.room_group_name:
            # Leave the board's room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Receive a message from WebSocket
    async def receive(self, text_data):
        if self.scope['user'] == AnonymousUser():
            # If the user is not authenticated, close the connection
            await self.close()
            return

        text_data_json = json.loads(text_data)
        action = text_data_json['action']

        # Send the message to all users in the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'board_update',
                'action': action,
            }
        )

    # Receive a message from the group
    async def board_update(self, event):
        action = event['action']

        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'action': action,
        }))
