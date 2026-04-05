from django.urls import path
from . import views

urlpatterns = [
    # 기존 코드들...
    path('', views.main_index, name='main_index'),
    path('auth/signup/', views.signup_view, name='signup'),
    path('auth/login/', views.login_view, name='login'),
    
    # [수정] 앞에 아무것도 안 붙이고 바로 /view/id/ 로 접속 가능하게 설정
    path('view/<str:message_id>/', views.view_message, name='view_message'),
    
    # API 관련
    path('api/messages/create/', views.MessageCreateView.as_view(), name='message_create'),
]