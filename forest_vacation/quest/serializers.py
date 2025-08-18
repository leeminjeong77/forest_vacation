from rest_framework import serializers
from .models import Quest, RandomQuest, Stamp

class QuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quest
        fields = ["id", "place", "reward_points", "description", "created_at"]

class RandomQuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RandomQuest
        fields = ["id", "quest", "status", "created_at", "updated_at"]

class StampSerializer(serializers.ModelSerializer):
    quest = QuestSerializer(read_only=True)

    class Meta:
        model = Stamp
        fields = ["id", "quest", "created_at"]
