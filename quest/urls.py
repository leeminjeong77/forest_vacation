from django.urls import path
from .views import (
    QuestListCreateView,
    QuestActionView,
    StampListView,
    DailyQuestView,
    RefreshRandomQuestView,
    DayResetView
    
    )

urlpatterns = [
    path("", QuestListCreateView.as_view(), name="quest-list-create"),
    path("stamps/", StampListView.as_view(), name="stamp-list"),
    path("daily/", DailyQuestView.as_view(), name="daily-quests"),
    path("refresh/", RefreshRandomQuestView.as_view(), name="refresh-random-quests"),
    path("day_reset/", DayResetView.as_view(), name="day-reset"),
    path("<int:pk>/", QuestActionView.as_view(), name="quest-action"),  # 마지막으로 이동
]


