from django.db import models
from user.models import User

class Reward(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='rewards/', blank=True, null=True)
    price = models.IntegerField(default=0)  # 교환에 필요한 포인트
    weight = models.IntegerField(default=0)  # 보상 확률 가중치
    created_at = models.DateTimeField(auto_now_add=True)

class UserReward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_rewards')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)