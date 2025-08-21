from django.db import models
from django.conf import settings
from django.utils import timezone

class Quest(models.Model):
    place = models.ForeignKey("place.Place", on_delete=models.CASCADE)
    reward_points = models.IntegerField(default=0)  # 포인트 보상
    description = models.TextField()

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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.RANDOM_LIST, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 상태 전환 허용 규칙
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
        constraints = [models.UniqueConstraint(fields=['user', 'quest'], name='uq_randomquest_user_quest')]

    def _set_status(self, new_status, *, extra_updates=None):
        """상태 전환 유효성 체크 후 변경"""
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
        """퀘스트 수락"""
        self._set_status(self.Status.ACCEPTED)

    def clear(self):
        """퀘스트 완료 처리: 스탬프 생성 + 포인트 지급 + 알림 생성"""
        from point.models import PointTransaction
        from notification.models import Notification

        self._set_status(self.Status.CLEAR)

        # 스탬프 생성 (중복 방지)
        stamp, created = Stamp.objects.get_or_create(user=self.user, quest=self.quest)

        # 포인트 지급 및 알림 발송
        points_added = 0
        if self.quest.reward_points > 0:
            PointTransaction.objects.create(user=self.user, amount=self.quest.reward_points, reason=f"퀘스트 완료: {self.quest.description}")
            Notification.objects.create(user=self.user, title="퀘스트 완료", content=f"{self.quest.reward_points} 포인트가 적립되었습니다.")
            points_added = self.quest.reward_points

        return {"stamp_created": created, "points_added": points_added, "notification": "퀘스트 완료 알림이 발송되었습니다." if points_added else None}

    def expire(self):
        """퀘스트 만료 처리"""
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
