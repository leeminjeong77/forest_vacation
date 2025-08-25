from rest_framework import serializers
from .models import ItemExchange
from reward.serializers import RewardSerializer
from user.serializers import UserSerializer

class ItemExchangeSerializer(serializers.ModelSerializer):
    reward = RewardSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ItemExchange
        fields = ['id', 'user', 'reward', 'is_used', 'exchanged_at', 'used_at']

class ItemExchangeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemExchange
        fields = ['reward'] 