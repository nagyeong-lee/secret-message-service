from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SecretMessage
from .serializers import SecretMessageSerializer
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required# 보안 데코레이터
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User

# --- 1. 화면(HTML)을 보여주는 기능 (프론트엔드) ---

# [메인 화면]
@login_required(login_url='/auth/login/')
def main_index(request):
    return render(request, 'index.html')


# [회원가입 로직]
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if username and password:
            User.objects.create_user(username=username, email=email, password=password)
            return redirect('/auth/login/')

    return render(request, 'auth/signup.html')


# [로그인 로직]
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('/')  # 로그인 성공하면 메인으로!
        else:
            return render(request, 'auth/login.html', {'error': '아이디나 비번이 틀렸어요!'})

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

            # 보안 핵심: 읽자마자 DB에서 바로 삭제
            response_data = serializer.data
            message.delete()

            return Response(response_data)
        except SecretMessage.DoesNotExist:
            return Response({"error": "이미 읽었거나 없는 메시지입니다."}, status=status.HTTP_404_NOT_FOUND)

        class MessageCreateView(APIView):
            permission_classes = [IsAuthenticated]  # 로그인 필수

            def post(self, request):
                content = request.data.get('content')  # 화면에서 쓴 글 가져오기

                if content:
                    # 1. DB 저장 (작성자 포함)
                    new_msg = SecretMessage.objects.create(
                        user=request.user,
                        content=content
                    )

                    # 2. 결과 응답 (상대방 확인용 주소까지 생성)
                    return Response({
                        "status": "success",
                        "message_id": new_msg.id,
                        "detail_url": f"/api/messages/{new_msg.id}/"  # 큐알에 들어갈 주소
                    }, status=status.HTTP_201_CREATED)

                return Response({"error": "내용 없음"}, status=status.HTTP_400_BAD_REQUEST)