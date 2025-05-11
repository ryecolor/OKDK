from django.urls import path
from .views import RegisterView, UserDetailView, DeleteAccountView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('user/', UserDetailView.as_view(), name='user_detail'),
    path('delete/', DeleteAccountView.as_view(), name='delete_account'),
]
