from django.db import models
from user.models import User
from place.models import Place
from django.db.models import Q
# Create your models here.

class Quest(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)  # 가게
    reward_points = models.IntegerField(default=0)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{getattr(self.place, 'name', '가게')} 사장님의 부탁({self.reward_points}P)"
    # 최신순 조회 최적화
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]

class RandomQuest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        status = "유효" if self.is_valid else "종료"
        return f"[{status}] u={self.user_id}, q={self.quest_id}"

    class Meta:
        # 유저별 유효 슬롯 조회 최적화
        indexes = [
            models.Index(fields=['user', 'is_valid']),
        ]
        # 퀘스트 중복 등록 방지 (퀘스트 3개 다르게)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'quest'],
                condition=Q(is_valid=True),
                name='uq_active_randomquest_per_user_quest',
            ),
        ]

class AcceptedQuest(models.Model):
    random_quest = models.ForeignKey(RandomQuest, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"RQ={self.random_quest_id}, 완료={self.is_verified}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_verified']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            # 진행중(False) 상태에서 같은 random_quest 중복 방지
            models.UniqueConstraint(
                fields=['random_quest'],
                condition=Q(is_verified=False),
                name='uq_active_accept_for_randomquest',
            ),
        ]