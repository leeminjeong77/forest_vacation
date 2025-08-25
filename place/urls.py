from django.urls import path
from .views import PlaceListCreateView, PlaceDetailView

urlpatterns = [
    # POST /places/ (등록), GET /places/ (목록)
    path('', PlaceListCreateView.as_view(), name='place-list'),
    # GET /places/{place_id} (단일)
    path('<int:pk>/', PlaceDetailView.as_view(), name='place-detail'),
]