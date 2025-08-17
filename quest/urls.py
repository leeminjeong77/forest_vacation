from django.urls import path
from .views import QuestListCreateView, QuestActionView, StampListView

urlpatterns = [
    path("", QuestListCreateView.as_view(), name="quest-list-create"),           
    path("<int:pk>/", QuestActionView.as_view(), name="quest-action"),
    path("stamps/", StampListView.as_view(), name="stamp-list"),
]
