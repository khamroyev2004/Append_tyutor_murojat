from django.db import models
from .manager import CustomUserManager
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        (1, 'Student'),
        (2, 'Tutor'),
    )
    full_name = models.CharField(max_length=150)
    hemis_id = models.CharField(max_length=14, unique=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=1)
    photo = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    def __str__(self):
        return self.username

class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return f'Tutor: {self.user.username}'
    class Meta:
        verbose_name = 'Tutor'
        verbose_name_plural = 'Tutors'

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return f'Student: {self.user.username}'
    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

class Group(models.Model):
    name = models.CharField(max_length=100)
    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='groups'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'