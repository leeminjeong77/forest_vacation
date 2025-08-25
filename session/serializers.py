from rest_framework import serializers
from .models import Session
from django.contrib.auth.hashers import make_password

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['id', 'user_id', 'status', 'turn_count', 'last_message_at', 'created_at', 'updated_at']
