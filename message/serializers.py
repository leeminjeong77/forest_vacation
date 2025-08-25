from rest_framework import serializers
from .models import Message
from django.contrib.auth.hashers import make_password

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'session', 'role', 'content', 'msg_seq', 'created_at', 'updated_at']
