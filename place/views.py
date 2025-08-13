from django.shortcuts import render

from rest_framework import generics
from .models import Place
from .serializers import PlaceSerializer

from rest_framework.permissions import AllowAny   # 임시

class PlaceListCreateView(generics.ListCreateAPIView):
    queryset = Place.objects.all().order_by('-id')
    serializer_class = PlaceSerializer
    permission_classes = [AllowAny]   # 임시


class PlaceDetailView(generics.RetrieveAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [AllowAny]   # 임시
