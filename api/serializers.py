from rest_framework import serializers
from main import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name',
            'email',
            'is_admin',
            'type',
            'last_login'
        )
        model = models.User
