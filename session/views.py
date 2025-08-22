from django.shortcuts import render
from openai import OpenAI

import forest_vacation.config2 as config2

from django.shortcuts import render
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Session
from message.models import Message
from message.models import Message as ChatMessage
from place.models import Place
from quest.models import Quest, RandomQuest
from user.models import User

from .serializers import SessionSerializer

from urllib.parse import urlparse

# Create your views here.

client = OpenAI(
	api_key = config2.OPENAI_API_KEY
)

system_instruction = """
  Please find 3 restaurants or cafes near Inha University in Korea that match the prompt I provide below.  
  The results must also exist in the list I give you.  
  There should be exactly 3 restaurants or cafes.  
  After you create the result, please present it in JSON format.  
  The names in the result must be from the provided list.

  Restaurants and Cafes List: {place_list}
  Context: {context}
  Question: {question}
  Answer: {answer}
"""


# Helper: call OpenAI to get three places (names) from the fixed list
def call_chatbot_and_pick_places(context: str, question: str, answer: str, candidates: list[str]) -> list:
	place_list_str = ", ".join(f'"{n}"' for n in candidates) if candidates else '""'
	
	prompt = system_instruction.format(context=context or "", question=question or "", answer=answer or "", place_list=place_list_str,)
  
	resp = client.responses.create(
		model="gpt-4o-mini",
		input=prompt,
		store=True,
	)
	
	# text = resp.output_text if hasattr(resp, "output_text") else (getattr(resp, "content", "") or "")
	text = getattr(resp, "output_text", None) or getattr(resp, "content", "") or ""

	# Very simple JSON-like name extraction fallback
	# candidates = ["육쌈냉면 인하대점", "면식당 인하대점", "백소정 인하대후문점"]
	picked = []
	for name in candidates:
		if name and name in text and name not in picked:
			picked.append(name)
			if len(picked) == 3:
				break
	if len(picked) < 3:
		remaining = [n for n in candidates if n not in picked]
		while len(picked) < 3 and remaining:
			picked.append(remaining.pop(0))  # 또는 random.choice/ random.sample
	return picked[:3]
	
	#picked = []
	#for name in candidates:
	#	if name in text and name not in picked:
	#		picked.append(name)
	#		if len(picked) == 3:
	#			break
	# # If model didn't echo names, just return all from the fixed list
	#if len(picked) < 3:
	#	picked = candidates[:3]
	# return picked


# Helper: ensure places and quests exist, then create RandomQuest entries and return info
def ensure_and_create_random_quests_for_user(user: User, place_names: list) -> list:
	results = []
	for name in place_names[:3]:
		place, _ = Place.objects.get_or_create(name=name)
		quest, _ = Quest.objects.get_or_create(
			place=place,
			defaults={
				"reward_points": 300,
				"description": f"{name}를 방문하고 인증하세요.",
			},
		)
		rq, _ = RandomQuest.objects.get_or_create(
			user=user,
			quest=quest,
			defaults={"status": RandomQuest.Status.RANDOM_LIST},
		)
		results.append({
			"random_quest_id": rq.id,
			"quest": place.name,
			"reward points": quest.reward_points,
			"description": quest.description,
		})
	return results


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_session(request):
	# In production, user would be from token; here we accept user_id for demo
	user = request.user
	user_id = user.id
	if not user_id:
		return Response({"success": False, "error": "user_id is required"}, status=400)
	try:
		user = User.objects.get(pk=user_id)
	except User.DoesNotExist:
		return Response({"success": False, "error": "user not found"}, status=404)

	session = Session.objects.create(user=user, status=True, turn_count=0, last_message_at=None)
	return Response({"success": True, "session_id": session.id})


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_answer(request):
	# Expected JSON: {"session_id", "user_id", "msg_seq", "context", "prompt"}
	data = request.data or {}
	session_id = data.get("session_id")
	user_id = data.get("user_id")
	msg_seq = int(data.get("msg_seq") or 1)
	context = data.get("context")
	prompt_text = data.get("prompt")
	candidates = list(Place.objects.values_list("name", flat=True))
	if not all([session_id, user_id, prompt_text]):
		return Response({"success": False, "error": "session_id, user_id, prompt are required"}, status=400)

	session = get_object_or_404(Session, id=session_id, user_id=user_id)

	# Save user message
	ChatMessage.objects.create(session=session, role=ChatMessage.Role.USER, content=prompt_text, msg_seq=msg_seq)
	session.turn_count = (session.turn_count or 0) + 1
	session.last_message_at = timezone.now()
	session.save(update_fields=["turn_count", "last_message_at"])

	# Call chatbot and create random quests now to be returned in end_session
	picked_names = call_chatbot_and_pick_places(
		context=context or "",
	  question=context or "",
	  answer=prompt_text or "",
	  candidates=candidates,)
	
	# picked_names = call_chatbot_and_pick_places(context=context or "", question=context or "", answer=prompt_text or "")
	created = ensure_and_create_random_quests_for_user(session.user, picked_names)

	return Response(created, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def end_session_and_recommend(request):
	# For demo, return three RANDOM_LIST quests created for the user today
	data = request.data or {}
	session_id = data.get("session_id")
	user_id = data.get("user_id")
	if not all([session_id, user_id]):
		return Response({"success": False, "error": "session_id, user_id are required"}, status=400)

	session = get_object_or_404(Session, id=session_id, user_id=user_id)
	user = session.user

	# Close session (optional for demo)
	session.status = False
	session.save(update_fields=["status"])

	# Collect or backfill three RANDOM_LIST for this user
	existing = list(RandomQuest.objects.filter(user=user, status=RandomQuest.Status.RANDOM_LIST)[:3])
	if len(existing) < 3:
		# Backfill using fixed list to ensure three
		backfill_names = ["육쌈냉면 인하대점", "면식당 인하대점", "백소정 인하대후문점"]
		needed = 3 - len(existing)
		created = ensure_and_create_random_quests_for_user(user, backfill_names)

	# Re-fetch up to 3
	rqs = list(RandomQuest.objects.filter(user=user, status=RandomQuest.Status.RANDOM_LIST)[:3])
	result = []
	for rq in rqs:
		result.append({
			"random_quest_id": rq.id,
			"quest": rq.quest.place.name,
			"reward points": rq.quest.reward_points,
			"description": rq.quest.description,
		})

	return Response(result) 
