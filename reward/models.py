from django.db import models

# Create your models here.
class reward(models.Model):
    name=models.CharField(max_length=100)
    image=models.ImageField(upload_to='rewards/', blank=True, null=True)
    price=models.IntegerField(default=0) # 교환에 필요한 포인트
    created_at=models.DateTimeField(auto_now_add=True)
    # 가중치는 추가 안했어용