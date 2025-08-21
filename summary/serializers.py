from rest_framework import serializers
from .models import Summary
from django.contrib.auth.hashers import make_password

class SummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = ['id', 'session_id', 'summary_text', 'sum_seq', 'created_at', 'updated_at']
