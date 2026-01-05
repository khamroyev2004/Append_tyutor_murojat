from django.db import models
from account.models import User
from django.utils import timezone

class Message(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Message from {self.sender.full_name} to {self.recipient.full_name} at {self.timestamp}'

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

class Message_File(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='files'
    )
    file = models.FileField(upload_to='message_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'File for message {self.message.id} uploaded at {self.uploaded_at}'
    class Meta:
        verbose_name = 'Message File'
        verbose_name_plural = 'Message Files'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payload = models.JSONField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)









