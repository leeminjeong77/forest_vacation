from django.db import models

from session.models import Session


# Create your models here.

class Summary(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="summaries")
    summary_text = models.TextField()
    sum_seq = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["session", "sum_seq"])]

    def __str__(self):
        return f"s={self.session_id} seq={self.sum_seq}" 