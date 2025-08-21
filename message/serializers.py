from rest_framework import serializers
from .models import Message
from django.contrib.auth.hashers import make_password

class SummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'session_id', 'role', 'content', 'msg_seq', 'created_at', 'updated_at']
