from rest_framework import serializers
from .models import Quest, RandomQuest, AcceptedQuest

class QuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quest
        fields = ['id', 'place', 'reward_points', 'description', 'created_at']

class AcceptedQuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcceptedQuest
        fields = ['id', 'random_quest', 'is_verified', 'created_at']
        read_only_fields = ['is_verified', 'created_at']

class AcceptedQuestVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = AcceptedQuest
        fields = ['is_verified']
