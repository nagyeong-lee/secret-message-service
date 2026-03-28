from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import SecretMessage
import qrcode
import io
import base64

# 1. 메인 화면
def main_index(request):
    # 이제 문자열이 아닌 index.html 파일을 렌더링합니다.
    # 로그인 여부는 템플릿(HTML) 안에서 {% if user.is_authenticated %}로 처리하는게 정석입니다.
    return render(request, 'index.html')

# 2. 회원가입 기능
@api_view(['POST', 'GET'])
def signup_view(request):
    if request.method == 'POST':
        username = request.data.get('username')
        email = request.data.get('email')
        phone = request.data.get('phone')
        password = request.data.get('password')
        password_confirm = request.data.get('password_confirm')
        
        # 1. 비밀번호 일치 확인
        if password != password_confirm:
            return HttpResponse('<script>alert("비밀번호가 일치하지 않습니다."); history.back();</script>')
            
        # 2. 아이디 중복 체크
        if User.objects.filter(username=username).exists():
            return HttpResponse('<script>alert("이미 존재하는 아이디입니다."); history.back();</script>')
            
        # 3. 사용자 생성
        User.objects.create_user(username=username, email=email, password=password)
        return redirect('/') 
    
    return render(request, 'signup.html')

# 3. 로그인 기능
@api_view(['POST', 'GET'])
def login_view(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return HttpResponse('<script>alert("아이디 또는 비밀번호가 틀렸습니다."); history.back();</script>')
            
    return render(request, 'login.html')

# 4. 메시지 생성 API (로그인 필수)
@api_view(['POST'])
def create_message(request):
    if not request.user.is_authenticated:
        return Response({"error": "로그인이 필요합니다."}, status=401)
    
    content = request.data.get('content')
    if not content:
        return Response({"error": "메시지 내용을 입력해주세요."}, status=400)
        
    # 메시지 객체 생성
    message = SecretMessage.objects.create(content=content)
    # 실제 접속할 주소 생성
    share_url = f"http://127.0.0.1:8000/api/message/{message.id}/"
    
    # QR 코드 생성 및 Base64 인코딩
    qr = qrcode.make(share_url)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    qr_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    return Response({
        "message": "비밀 메시지가 생성되었습니다.",
        "url": share_url,
        "qr_code": f"data:image/png;base64,{qr_base64}"
    })

# 5. 메시지 조회 (읽는 순간 삭제!)
def view_message(request, message_id):
    if not request.user.is_authenticated:
        return render(request, 'login_required.html') # 로그인이 필요하다는 안내 페이지
        
    message = get_object_or_404(SecretMessage, id=message_id)
    content = message.content
    
    # 🔥 조회 즉시 DB에서 삭제 (휘발성 핵심 로직)
    message.delete()
    
    return render(request, 'view_message.html', {'content': content})