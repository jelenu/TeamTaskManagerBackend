from django.http import JsonResponse
from django.views import View
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Board, BoardAccess
import json

User = get_user_model()

class AuthenticatedView(View):
    def authenticate_user(self, token):
        """
        Authenticate the user using the JWT token provided by `rest_framework_simplejwt`.
        """
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
        except (InvalidToken, TokenError, User.DoesNotExist):
            return None

    def get_authenticated_user(self, request):
        """
        Get the authenticated user from the request cookies.
        """
        auth_token = request.COOKIES.get('accessToken')
        if not auth_token:
            return None, JsonResponse({'message': 'No authentication token provided'}, status=401)
        
        user = self.authenticate_user(auth_token)
        if not user:
            return None, JsonResponse({'message': 'Invalid authentication token'}, status=401)
        
        return user, None


class UserBoardsView(AuthenticatedView):
    def get(self, request):
        user, error_response = self.get_authenticated_user(request)
        if error_response:
            return error_response
        
        boards = Board.objects.filter(users=user).values('id', 'name')
        return JsonResponse({'boards': list(boards)}, status=200)
    

class CreateBoardView(AuthenticatedView):
    def post(self, request):
        user, error_response = self.get_authenticated_user(request)
        if error_response:
            return error_response

        try:
            # Parse JSON body
            data = json.loads(request.body)
            board_name = data.get('name')
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)

        # Verify board name not empty
        if not board_name:
            return JsonResponse({'message': 'Board name cannot be empty'}, status=400)

        # Create new board
        board = Board.objects.create(name=board_name)

        # Associate the user as the creator of the board
        BoardAccess.objects.create(user=user, board=board, role='creator')
        
        response_data = {
            'board_id': board.id,
            'board_name': board.name,
        }

        return JsonResponse(response_data, status=201)

class AddUserToBoardView(AuthenticatedView):
    def post(self, request):
        user, error_response = self.get_authenticated_user(request)
        if error_response:
            return error_response

        # Parsear los datos del body
        try:
            data = json.loads(request.body)
            board_id = data.get('board_id')
            user_name = data.get('user_name')
            role = data.get('role')
        except (ValueError, KeyError):
            return JsonResponse({'message': 'Invalid request body or missing fields'}, status=400)

        # Validar role
        if role not in ['standard', 'coordinator']:
            return JsonResponse({'message': 'Invalid role. Must be either "standard" or "coordinator"'}, status=400)

        # Obtener board y user por los datos del body
        board = get_object_or_404(Board, id=board_id)
        user_to_add = get_object_or_404(User, username=user_name)

        # Verificar si el usuario autenticado tiene permisos para agregar usuarios
        board_access = BoardAccess.objects.filter(board=board, user=user)
        if not board_access.exists() or board_access.first().role not in ['creator', 'coordinator']:
            return JsonResponse({'message': 'You do not have permission to add users to this board'}, status=403)

        # Verificar si el usuario ya está en el board
        if BoardAccess.objects.filter(board=board, user=user_to_add).exists():
            return JsonResponse({'message': 'User is already on the board'}, status=400)

        # Crear acceso del usuario con el rol especificado
        BoardAccess.objects.create(user=user_to_add, board=board, role=role)

        # Notificar al usuario via WebSocket
        channel_layer = get_channel_layer()
        notification_message = f"You have been added to the board '{board.name}' as a {role}."

        async_to_sync(channel_layer.group_send)(
            f'user_{user_to_add.id}',
            {
                'type': 'notify_user',
                'message': notification_message
            }
        )

        return JsonResponse({'message': f'User {user_to_add.username} added to the board {board.name} with role {role}'}, status=200)

