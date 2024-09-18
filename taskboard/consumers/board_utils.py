from taskboard.models import Board, BoardAccess, List
from channels.db import database_sync_to_async
from .authentication import user_has_access

@database_sync_to_async
def get_board_lists(board_id):
    """
    Get lists for a board, including its tasks and comments.
    """
    board = Board.objects.prefetch_related('lists__tasks__comments').get(id=board_id)

    board_data = []
    for list_ in board.lists.all():
        tasks_data = []
        for task in list_.tasks.all():
            comments_data = list(task.comments.values('id', 'user_id', 'text', 'created_at'))

            tasks_data.append({
                'id': task.id,
                'name': task.name,
                'order': task.order,
                'assigned': list(task.assigned.values('id', 'username')),
                'creator': task.creator_id,
                'comments': comments_data
            })

        board_data.append({
            'id': list_.id,
            'name': list_.name,
            'order': list_.order,
            'tasks': tasks_data
        })

    return board_data


async def get_board_users(board_id, current_user):
    """Get the users with their roles for a specific board, excluding the current user."""
    
    # Get board access for users, excluding the current user
    board_access = await database_sync_to_async(BoardAccess.objects.filter)(board_id=board_id)
    
    # List of users with their roles, excluding the current user
    users_with_roles = await database_sync_to_async(
        lambda: [{'username': ba.user.username, 'role': ba.role}
                 for ba in board_access.select_related('user') if ba.user != current_user]
    )()
    
    # Get the current user's role
    current_user_role = await database_sync_to_async(
        lambda: board_access.get(user=current_user).role
    )()
    
    return users_with_roles, current_user_role

