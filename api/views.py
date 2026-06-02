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
from django.core.exceptions import ValidationError
from django.utils import timezone  # 타이머


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


# [비밀 메시지 확인 화면] - 타이머 폭파 기능
def view_message(request, message_id):
    """
    사용자가 QR 코드를 찍고 들어왔을 때 메시지를 보여주는 함수.
    설정한 시간이 지났거나, 이미 삭제된 경우 안내 문구를 출력합니다.
    """
    try:
        # 1. DB에서 메시지 조회
        message = SecretMessage.objects.get(pk=message_id)

        # 2. [보안 고도화] 현재 시간 - 생성 시간이 설정한 유지 시간(초)을 넘었는지 계산
        time_passed = (timezone.now() - message.created_at).total_seconds()

        if time_passed > message.duration:
            # 설정한 제한 시간이 지나면 화면을 안 보여주고 즉시 DB에서 삭제
            message.delete()
            return render(request, 'view_message.html', {
                'error': "제한 시간이 초과되어 이미 사라진 메시지입니다. "
            })

        # 3. 아직 유효 시간 안쪽이라면 내용을 가져오고 즉시 삭제 (휘발성 1회 열람 보안)
        content = message.content
        message.delete()

        return render(request, 'view_message.html', {'content': content})

    except (SecretMessage.DoesNotExist, ValidationError):
        # 4. 메시지가 없거나 이미 삭제된 경우 (또는 유효하지 않은 ID인 경우)
        return render(request, 'view_message.html', {
            'error': "이미 확인했거나 존재하지 않는 비밀 메시지입니다"
        })


# --- 2. 데이터 처리(API) 기능 ---

# [메시지 생성 API]
class MessageCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        content = request.data.get('content')

        # [타이머 추가]  화면에서 보낸 'duration' 값을 가져옴 (안 보내주면 기본 60초)
        duration = request.data.get('duration', 60)

        if content:
            new_msg = SecretMessage.objects.create(
                user=request.user,
                content=content,
                duration=int(duration)  # 아까 models.py에 만든 필드에 숫자로 변환해서 저장!
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