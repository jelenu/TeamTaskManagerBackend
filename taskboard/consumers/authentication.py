import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from taskboard.models import BoardAccess

User = get_user_model()

def validate_jwt_token(token):
    """
    Decode and validate the JWT token.
    """
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired.')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token.')

@database_sync_to_async
def get_user(user_id):
    """
    Get the user from the database by ID.
    """
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

@database_sync_to_async
def user_has_access(board_id, user):
    """
    Check if the user has access to the board.
    """
    return BoardAccess.objects.filter(board_id=board_id, user=user).exists()
