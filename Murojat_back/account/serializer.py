from rest_framework import serializers
from .models import User


class TutorSerializer(serializers.ModelSerializer):
    photo = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'full_name',
            'hemis_id', 
            'role',
            'photo',
            'is_active',
            'created_at',
            'group',
        ]

class HemisUniversalSerializer(serializers.Serializer):
    hemis_id = serializers.CharField(max_length=14)



class CreatePasswordSerializer(serializers.Serializer):
    hemis_id = serializers.CharField(max_length=14)
    password = serializers.CharField(write_only=True)

    def validate_hemis_id(self, value):
        if not User.objects.filter(hemis_id=value).exists():
            raise serializers.ValidationError(
                "User with this HEMIS ID does not exist."
            )
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        return value


    
class LoginSerializer(serializers.Serializer):
    hemis_id = serializers.CharField(max_length=14)
    password = serializers.CharField(write_only=True)
    class Meta:
        model : User
        fields = [
            'hemis_id',
            'password'
            ]
        
    def validate(self, data):
        hemis_id = data.get("hemis_id")
        password = data.get("password")
        try:
            user = User.objects.get(hemis_id=hemis_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid HEMIS ID or password.")
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid HEMIS ID or password.")
        if not user.is_active:
            raise serializers.ValidationError("User account is not active.")
        data["user"] = user
        return data