from django.urls import path
from . import views

urlpatterns = [
    path("quest/complete/", views.QuestCompleteView.as_view()),
    path("voucher/use/", views.VoucherUseView.as_view()),
    path("", views.PointTransactionListView.as_view()),
]