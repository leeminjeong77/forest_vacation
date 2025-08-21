from django.urls import path
from . import views  # OK: urls -> views (단방향)

urlpatterns = [
    # path("", views.summary_list, name="summary-list"),  # 예시
    # path("detail/<int:pk>/", views.summary_detail, name="summary-detail"),
]