from django.db import models

from user.models import User

# Create your models here.

class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    status = models.BooleanField(default=True) # false : 끝난 세션
    turn_count = models.IntegerField()
    last_message_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 
    
