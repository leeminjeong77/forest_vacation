from django.db import models
from user.models import User
# Create your models here.

class PointTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_transactions')
    amount = models.IntegerField()  # +면 적립, -면 차감
    reason = models.CharField(max_length=255, blank=True, null=True)  # 변경 이유(예: 퀘스트 완료 보상 등)
    created_at = models.DateTimeField(auto_now_add=True)
