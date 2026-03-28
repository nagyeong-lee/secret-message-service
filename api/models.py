from django.db import models
import uuid

class SecretMessage(models.Model):
    # 보안을 위해 무작위 문자열(UUID)을 주소로 사용합니다.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField() # 메시지 내용
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False) # 읽음 여부

    def __str__(self):
        return f"Message {self.id}"