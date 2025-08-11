from django.db import models
from user.models import User
from place.models import Place
# Create your models here.

class Quest(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)  # 가게
    reward_points = models.IntegerField(default=0)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class RandomQuest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    is_valid = models.BooleanField(default=True)

class AcceptedQuest(models.Model):
    random_quest = models.ForeignKey(RandomQuest, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)