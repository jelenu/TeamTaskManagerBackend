from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Registro del modelo de usuario personalizado
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Opcional: Personaliza cómo se muestra el usuario en el admin
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'username')
