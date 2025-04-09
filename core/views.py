import datetime
import jwt
import json
import openai
from openai import OpenAI
import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .mongo import users_collection
from .utils import jwt_required

openai.api_key = os.getenv("OPENAI_API_KEY")



@csrf_exempt
@jwt_required
def protected_view(request):
    return JsonResponse({"msg": f"Hello {request.user_email}, you're authenticated!"})

def test_mongo(request):
    users_collection.insert_one({"name": "Test User"})
    return JsonResponse({"msg": "Mongo connected and user added!"})

def generate_jwt(email):
    payload = {
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

@method_decorator(csrf_exempt, name='dispatch')
class SignupView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        if users_collection.find_one({"email": email}):
            return JsonResponse({"error": "User already exists"}, status=400)

        hashed_pwd = make_password(password)
        users_collection.insert_one({
            "email": email,
            "password": hashed_pwd
        })

        token = generate_jwt(email)
        return JsonResponse({"token": token})

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        user = users_collection.find_one({"email": email})
        if not user or not check_password(password, user["password"]):
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        token = generate_jwt(email)
        return JsonResponse({"token": token})


@api_view(['POST'])
def generate_website(request):
    prompt = request.data.get("prompt")
    if not prompt:
        return Response({"error": "Prompt is required"}, status=400)

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates HTML websites."},
                {"role": "user", "content": f"Generate a responsive HTML and CSS website for this prompt: {prompt}"}
            ],
            max_tokens=2000,
            temperature=0.7,
        )

        generated_html = response.choices[0].message.content

        return Response({"html": generated_html})
    except Exception as e:
        return Response({"error": str(e)}, status=500)
