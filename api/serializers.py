from rest_framework import serializers
from .models import SecretMessage

class SecretMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecretMessage
        # 모든 필드(id, content, created_at, is_read)를 다 사용하겠다는 뜻
        fields = '__all__'