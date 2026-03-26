from django.http import JsonResponse

def test_api(request):
    # 'ensure_ascii': False 를 추가하면 한글이 유니코드로 변환되지 않고 그대로 나옵니다!
    return JsonResponse(
        {"message": "백엔드 서버와 연결 성공! "},
        json_dumps_params={'ensure_ascii': False}
    )