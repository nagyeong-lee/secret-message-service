from django.urls import path
from .views import MessageCreateView, MessageDetailView

urlpatterns = [
    # 팀원들이 만든 API 경로들
    path('', MessageCreateView.as_view(), name='message-create'),
    path('message/<uuid:pk>/', MessageDetailView.as_view(), name='message-detail'),
]