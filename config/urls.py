from django.contrib import admin
from django.urls import path, include
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.main_index, name='main_index'),
    # 1. 프론트엔드 화면 (회원가입, 로그인)
    path('auth/signup/', views.signup_view, name='signup'),
    path('auth/login/', views.login_view, name='login'),

    # 2. 백엔드 API (팀원이 만든 기능)
    path('api/', include('api.urls')), 
]