from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SecretMessage
from .serializers import SecretMessageSerializer
from django.core.exceptions import ValidationError # 추가

# --- 1. 화면(HTML) 렌더링 기능 ---

# [메인 화면]
@login_required(login_url='/auth/login/')
def main_index(request):
    return render(request, 'index.html')

# [회원가입]
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if username and password:
            User.objects.create_user(username=username, email=email, password=password)
            return redirect('/auth/login/')
    return render(request, 'auth/signup.html')

# [로그인]
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('/')
        else:
            return render(request, 'auth/login.html', {'error': '아이디나 비밀번호가 틀렸습니다.'})
    return render(request, 'auth/login.html')

# [비밀 메시지 확인 화면] - 에러 핸들링 강화 버전
def view_message(request, message_id):
    """
    사용자가 QR 코드를 찍고 들어왔을 때 메시지를 보여주는 함수.
    읽는 순간 삭제되며, 이미 삭제된 경우 안내 문구를 출력합니다.
    """
    try:
        # 1. DB에서 메시지 조회
        message = SecretMessage.objects.get(pk=message_id)
        content = message.content
        
        # 2. 보안 핵심: 보여주기 직전 DB에서 즉시 삭제 (휘발성)
        message.delete()
        
        return render(request, 'view_message.html', {'content': content})

    except (SecretMessage.DoesNotExist, ValidationError):
        # 3. 메시지가 없거나 이미 삭제된 경우 (또는 유효하지 않은 ID인 경우)
        return render(request, 'view_message.html', {
            'error': "이미 확인했거나 존재하지 않는 비밀 메시지입니다! 💣"
        })


# --- 2. 데이터 처리(API) 기능 ---

# [메시지 생성 API]
class MessageCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        content = request.data.get('content')
        if content:
            new_msg = SecretMessage.objects.create(
                user=request.user,
                content=content
            )
            return Response({
                "status": "success",
                "secret_url": f"/view/{new_msg.id}/"
            }, status=status.HTTP_201_CREATED)
        
        return Response({"error": "내용이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

# [메시지 상세 정보 API]
class MessageDetailView(APIView):
    def get(self, request, pk):
        try:
            message = SecretMessage.objects.get(pk=pk)
            serializer = SecretMessageSerializer(message)
            response_data = serializer.data
            message.delete() 
            return Response(response_data)
        except SecretMessage.DoesNotExist:
            return Response({"error": "이미 읽었거나 없는 메시지입니다."}, status=status.HTTP_404_NOT_FOUND)