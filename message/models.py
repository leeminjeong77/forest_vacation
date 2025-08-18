from django.db import models

from user.models import User

# Create your models here.

class Message(models.Model):
    session = models.ForeignKey(User, on_delete=models.CASCADE, related_name="summaries")
    role = models.enums
    # USER, AI
    content = models.TextField()
    msg_seq = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 