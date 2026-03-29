from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SecretMessage
from .serializers import SecretMessageSerializer


# 1. 메시지 저장 기능
class MessageCreateView(APIView):
    def post(self, request):
        serializer = SecretMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 2. 메시지 읽기 및 즉시 삭제 (일회성)
class MessageDetailView(APIView):
    def get(self, request, pk):
        try:
            message = SecretMessage.objects.get(pk=pk)
            serializer = SecretMessageSerializer(message)

            # 읽자마자 DB에서 바로 삭제 (폭파 기능)
            response_data = serializer.data
            message.delete()

            return Response(response_data)
        except SecretMessage.DoesNotExist:
            return Response({"error": "이미 읽었거나 없는 메시지입니다."}, status=status.HTTP_404_NOT_FOUND)