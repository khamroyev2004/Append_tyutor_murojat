from rest_framework import serializers
from .models import *

class MessageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message_File
        fields = [
            'id',
            'file',
        ]
class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    files = MessageFileSerializer(many=True, read_only=True)
    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "recipient",
            "content",
            "timestamp",
            "files",
        ]
    def get_sender(self, obj):
        return {
            "id": obj.sender.id,
            "full_name": obj.sender.full_name,
            "photo": obj.sender.photo,
        }