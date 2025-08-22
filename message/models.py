from django.db import models

from session.models import Session

# Create your models here.

class Message(models.Model):
    class Role(models.TextChoices):
        USER = "USER", "USER"
        AI = "AI", "AI"

    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=8, choices=Role.choices, db_index=True)
    # USER, AI
    content = models.TextField()
    msg_seq = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["session", "msg_seq"])]

    def __str__(self):
        return f"[{self.role}] s={self.session_id} seq={self.msg_seq}" 