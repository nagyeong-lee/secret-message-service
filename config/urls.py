from django.contrib import admin
from django.urls import path
from api.views import main_index, create_message, view_message, signup_view, login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_index),
    path('auth/signup/', signup_view),
    path('auth/login/', login_view),
    path('auth/logout/', lambda r: [logout(r), redirect('/')][1]), # 로그아웃 후 메인으로
    path('api/create/', create_message),
    path('api/message/<uuid:message_id>/', view_message),
]
