import uuid
from django.db import models
from django.contrib.auth.models import User


class SecretMessage(models.Model):
    # 1. 보안을 위해 숫자 대신 무작위 문자열(UUID) 사용
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # 2. 누가 썼는지 (User 모델과 연결)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # 3. 메시지 내용 및 상태
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message {self.id}"