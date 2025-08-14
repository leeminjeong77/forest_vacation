from django.urls import path
from . import views

urlpatterns = [
    path("", views.UserRewardListView.as_view()),
    path("<int:pk>/", views.UserRewardUseView.as_view()),
]