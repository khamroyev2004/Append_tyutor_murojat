from django.urls import path
from .views import *

urlpatterns = [
    path('send-message/', send_message, name='send_message'),
    path('dialog/<int:user_id>/', dialog, name='get_dialog'),
]