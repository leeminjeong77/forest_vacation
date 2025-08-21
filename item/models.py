from django.db import models
from user.models import User
from reward.models import Reward
# Create your models here.
from django.conf import settings

class ItemExchange(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='item_exchanges')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE, related_name='item_exchanges')
    is_used = models.BooleanField(default=False)
    exchanged_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'reward']
        ordering = ['-exchanged_at']
    
    def __str__(self):
        return f"{self.user.username}의 {self.reward.name}"

