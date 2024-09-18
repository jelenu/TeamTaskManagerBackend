import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import AuthenticationFailed
from .authentication import validate_jwt_token, get_user, user_has_access
from .board_utils import get_board_lists, get_board_users
from taskboard.models import Board, List
from channels.db import database_sync_to_async

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

        # Send lists and users to the user
        lists = await get_board_lists(self.board_id)
        users, user_role = await get_board_users(self.board_id, user)

        await self.send(text_data=json.dumps({
            'type': 'initial_data',
            'lists': lists,
            'users': users,
            'role': user_role
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

        if action == 'create_list':
            # Get the data for the new list
            list_name = text_data_json.get('name')

            if not list_name:
                return

            # Create the new list in the database
            new_list = await self.create_list(list_name, self.board_id, self.scope['user'])

            # If the list was successfully created, propagate the event to all users
            if new_list:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'board_update',
                        'action': 'new_list',
                        'list': {
                            'id': new_list.id,
                            'name': new_list.name,
                            'order': new_list.order
                        }
                    }
                )

    async def board_update(self, event):
        action = event['action']

        # Check if it's a new list action
        if action == 'new_list':
            list_data = event['list']

            # Send the new list data to the connected users
            await self.send(text_data=json.dumps({
                'action': 'new_list',
                'list': list_data
            }))

    async def create_list(self, name, board_id, user):
        board = await database_sync_to_async(Board.objects.get)(id=board_id)

        # Check if the user has access to the board
        if not await user_has_access(board.id, user):
            return None

        # Create the list in the database
        last_order = await database_sync_to_async(List.objects.filter(board=board).count)()
        new_list = await database_sync_to_async(List.objects.create)(
            name=name,
            board=board,
            order=last_order + 1
        )

        return new_list


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Initialize room_group_name with a default value
        self.user_group_name = None

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
        self.user_group_name = f'user_{user.id}'

        # Join the user's notification group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        if self.user_group_name:
            # Leave the user's notification group
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    async def notify_user(self, event):
        message = event['message']

        # Send the notification message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': message
        }))
