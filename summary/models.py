from django.db import models

from session.models import Session


# Create your models here.

class Summary(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="summaries")
    summary_text = models.TextField()
    sum_seq = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 