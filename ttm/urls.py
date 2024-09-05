
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from users.views import UserActivationView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/token/', include('djoser.urls.jwt')),
    path('auth/users/activation/<str:uid>/<str:token>/', UserActivationView.as_view()),

]

