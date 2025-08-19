from django.urls import path
from .views import ReceiptUploadView

urlpatterns = [
    path("", ReceiptUploadView.as_view(), name="receipt-upload"),
]