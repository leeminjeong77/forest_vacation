from rest_framework import serializers
from .models import Reward, UserReward

class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = ['id', 'name', 'image', 'price', 'created_at']

class UserRewardSerializer(serializers.ModelSerializer):
    reward = RewardSerializer()
    class Meta:
        model = UserReward
        fields = ['id', 'reward', 'is_used', 'created_at', 'used_at']

class RewardUseSerializer(serializers.Serializer):
    user_reward_id = serializers.IntegerField()