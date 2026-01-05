from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

router = DefaultRouter()
router.register(r'check-user', ApiCheckStudent, basename='check-user')

urlpatterns = [
    path('', include(router.urls)),
    path('create-password/',auth, name='create-password'),
    path('list-groups/', list_groups, name='list_groups'),
    path('logout/', logout, name='logout'),
]
