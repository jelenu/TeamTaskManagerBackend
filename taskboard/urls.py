from django.urls import path
from .views import UserBoardsView, AddUserToBoardView, CreateBoardView

urlpatterns = [
    path('boards/', UserBoardsView.as_view(), name='user-boards'),
    path('boards/create/', CreateBoardView.as_view(), name='create-board'),
    path('boards/add_user/', AddUserToBoardView.as_view(), name='add_user_to_board'),
]
