from django.urls import path, include
from .views import UserRegister, Login

urlpatterns = [
    path('', UserRegister.as_view(),  name='registeruser'),
    path('', Login.as_view(),  name='signinuser'),
]