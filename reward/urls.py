from django.urls import path
from . import views

urlpatterns = [
    path("", views.user_reward_list),
    path("create/", views.create_reward),
    path("all/", views.reward_list),
    path("draw/", views.draw_reward),
    path("<int:pk>/", views.use_user_reward),
]