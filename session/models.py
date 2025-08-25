from django.db import models

from user.models import User

# Create your models here.

class Session(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
	status = models.BooleanField(default=True) # false : 끝난 세션
	turn_count = models.IntegerField(default=0)
	last_message_at = models.DateTimeField(null=True, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		indexes = [models.Index(fields=["user", "status"])]

	def __str__(self):
		return f"session={self.id} user={self.user_id} active={self.status}" 
    
