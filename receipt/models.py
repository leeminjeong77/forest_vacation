from django.db import models
from django.conf import settings

class Receipt(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "대기"
        SUCCESS = "SUCCESS", "성공"
        FAILURE = "FAILURE", "실패"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="receipts")
    quest = models.ForeignKey("quest.Quest", on_delete=models.CASCADE, related_name="receipts", null=True, blank=True) # 임시 null 허용

    image = models.ImageField(upload_to="receipts/")

    ocr_uid = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    message = models.TextField(blank=True, null=True)

    store_name = models.CharField(max_length=200, blank=True, null=True)
    total_price = models.IntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.store_name or '영수증'} - {self.user}"