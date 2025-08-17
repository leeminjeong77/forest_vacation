from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Q

class Quest(models.Model):
    place = models.ForeignKey("place.Place", on_delete=models.CASCADE)  # 문자열 참조
    reward_points = models.IntegerField(default=0)
    description = models.TextField()

    # 도감용 이미지
    image = models.ImageField(upload_to="quests/", blank=True, null=True)  # ✅ 도감용 이미지

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['created_at'])]

    def __str__(self):
        return f"{getattr(self.place, 'name', '가게')} 사장님의 부탁({self.reward_points}P)"


class RandomQuest(models.Model):
    class Status(models.TextChoices):
        RANDOM_LIST = "RANDOM_LIST", "노출 퀘스트"
        EXPIRED     = "EXPIRED",     "만료 퀘스트"
        ACCEPTED    = "ACCEPTED",    "수락 퀘스트"
        CLEAR       = "CLEAR",       "완료 퀘스트"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 문자열/설정 사용
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    status = models.CharField(max_length=12, choices=Status.choices,
                              default=Status.RANDOM_LIST, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 상태 전이 허용표
    ALLOWED_TRANSITIONS = {
        Status.RANDOM_LIST: {Status.ACCEPTED, Status.EXPIRED},
        Status.ACCEPTED:    {Status.CLEAR, Status.EXPIRED},
        Status.CLEAR:       set(),
        Status.EXPIRED:     set(),
    }

    def __str__(self):
        return f"[{self.status}] u={self.user_id}, q={self.quest_id}"

    class Meta:
        indexes = [models.Index(fields=['user', 'status'])]
        constraints = [
            models.UniqueConstraint(fields=['user', 'quest'], name='uq_randomquest_user_quest'),
        ]

    # 전이 로직
    def _set_status(self, new_status, *, extra_updates=None):
        cur = self.status
        if new_status not in self.ALLOWED_TRANSITIONS.get(cur, set()):
            raise ValueError(f"Invalid transition: {cur} -> {new_status}")
        self.status = new_status
        self.updated_at = timezone.now()
        update_fields = ['status', 'updated_at']
        if extra_updates:
            for k, v in extra_updates.items():
                setattr(self, k, v)
                update_fields.append(k)
        self.save(update_fields=update_fields)

    def accept(self):
        self._set_status(self.Status.ACCEPTED)

    def clear(self):
        self._set_status(self.Status.CLEAR)
        Stamp.objects.get_or_create(user=self.user, quest=self.quest)

    def expire(self):
        self._set_status(self.Status.EXPIRED)


class Stamp(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stamps')
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='stamps')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'quest')
        ordering = ['-created_at']

    def __str__(self):
        return f"Stamp u={self.user_id}, q={self.quest_id}"