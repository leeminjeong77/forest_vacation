from django.urls import path
from .views import QuestCreateView, QuestActionView

urlpatterns = [
    path('', QuestCreateView.as_view(), name='quest-create'),
    path('<int:pk>/', QuestActionView.as_view(), name='quest-action'),
]
