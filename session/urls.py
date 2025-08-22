from django.urls import path
from . import views

urlpatterns = [
	path("start/", views.create_session),
	path("answer/", views.submit_answer),
	path("end/", views.end_session_and_recommend),
]