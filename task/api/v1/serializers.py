from django.contrib.auth import get_user_model
from rest_framework import serializers
from ...models import Task

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class TaskSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'completed', 'owner', 'created_at', 'updated_at')
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')
