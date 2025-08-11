from django.db import models
from django.conf import settings

# Create your models here.

class Quest(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    reward_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class UserQuest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),   # 생성됨, 수락 전
        ('accepted', 'Accepted'), # 사용자가 수락함
        ('completed', 'Completed'), # 완료됨
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    accepted_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.quest} ({self.status})"