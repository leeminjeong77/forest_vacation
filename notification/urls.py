from django.urls import path
from . import views

urlpatterns = [
    path("", views.notification_list),
    path("<int:notification_id>/",views.mark_notification_read),
    path("delete/", views.delete_read_notifications),
]