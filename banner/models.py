from django.db import models

# Create your models here.

class BannerAd(models.Model):
    title = models.CharField(max_length=100)         
    image = models.ImageField(upload_to="ads/")       
    type = models.CharField(max_length=50)            # 배너 유형 (예: "광고", "프로모션" 등)
    created_at = models.DateTimeField(auto_now_add=True) 
