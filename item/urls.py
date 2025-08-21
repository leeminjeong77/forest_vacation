from django.urls import path
from . import views

urlpatterns = [
    path("all/", views.all_items, name="all_items"),
    path("exchange/", views.exchange_item, name="exchange_item"),
    path("my/", views.user_items, name="user_items"),
    path("<int:pk>/use/", views.use_item, name="use_item"),
] 