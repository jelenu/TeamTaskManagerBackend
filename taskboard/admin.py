from django.contrib import admin
from .models import Board, BoardAccess, List, Task, Comment

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator')
    search_fields = ('name',)

@admin.register(BoardAccess)
class BoardAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'board', 'role')
    list_filter = ('role',)

@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ('name', 'board', 'order')
    search_fields = ('name',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'list', 'creator', 'order')
    search_fields = ('name',)
    filter_vertical = ('assigned',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'created_at')
    search_fields = ('text',)
    list_filter = ('created_at',)
