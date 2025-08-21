from django.shortcuts import render
from openai import OpenAI

import config

from django.shortcuts import render
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from .models import Session

import uuid #고유한 이름 만들어줌
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .serializers import SessionSerializer

from urllib.parse import urlparse

# Create your views here.

client = OpenAI(
	api_key = config.OPENAI_API_KEY
)

response = client.responses.create(
  model="gpt-4o-mini",
  input="write a haiku about ai",
  store=True,
)

# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_preset_questions(request):

@api_view(['POST'])
@permission_classes([AllowAny])
def create_session(request):
    if request.method == 'POST':
        user_id = request.data.get("user_id")
        serializer = SessionSerializer(data = {})
        return 2
    else:
        return 1 
