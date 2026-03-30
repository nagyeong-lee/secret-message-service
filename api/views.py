from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SecretMessage
from .serializers import SecretMessageSerializer
from django.shortcuts import render, redirect

# --- 1. 화면(HTML)을 보여주는 기능 (프론트엔드) ---

# [추가] 접속하자마자 보이는 휘발성 메시지 메인 화면
def main_index(request):
    # api/templates/index.html 파일을 찾아 화면에 띄웁니다.
    return render(request, 'index.html')

# 회원가입 화면
def signup_view(request):
    return render(request, 'auth/signup.html')

# 로그인 화면
def login_view(request):
    return render(request, 'auth/login.html')


# --- 2. 데이터를 처리하는 기능 (백엔드 API) ---

# 메시지 저장 (POST)
class MessageCreateView(APIView):
    def post(self, request):
        serializer = SecretMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 메시지 읽기 및 폭파 (GET)
class MessageDetailView(APIView):
    def get(self, request, pk):
        try:
            message = SecretMessage.objects.get(pk=pk)
            serializer = SecretMessageSerializer(message)

            # 읽자마자 DB에서 바로 삭제
            response_data = serializer.data
            message.delete()

            return Response(response_data)
        except SecretMessage.DoesNotExist:
            return Response({"error": "이미 읽었거나 없는 메시지입니다."}, status=status.HTTP_404_NOT_FOUND)