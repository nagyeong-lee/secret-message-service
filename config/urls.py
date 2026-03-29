from django.contrib import admin
from django.urls import path
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # 메시지 생성 (POST)
    path('api/create/', views.MessageCreateView.as_view(), name='message-create'),

    # 메시지 읽기 및 삭제 (GET)
    path('api/message/<uuid:pk>/', views.MessageDetailView.as_view(), name='message-detail'),
]