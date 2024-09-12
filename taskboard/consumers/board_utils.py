from taskboard.models import Board
from channels.db import database_sync_to_async


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
