from django.urls import path
from . import views

urlpatterns = [
    path("quest/complete/", views.quest_complete),
    path("voucher/use/", views.voucher_use),
    path("", views.point_transaction_list),
]