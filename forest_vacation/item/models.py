from django.db import models
from user.models import User
from reward.models import Reward
# Create your models here.
from django.conf import settings

class ItemExchange(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)
    exchanged_at = models.DateTimeField(auto_now_add=True)

