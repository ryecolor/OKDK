from django.db import models
from django.contrib.auth.models import AbstractUser
from region.models import District

class CustomUser(AbstractUser):
    # 사용자 이름 필드
    username = models.CharField(max_length=150, unique=True)
    # user_profile = models.ImageField()
    
    # 비밀번호 필드는 AbstractUser에서 자동으로 제공됨
    # 관리구역 필드 추가
    district = models.CharField(max_length=100)
    district_id = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, related_name='user_profiles')
    def __str__(self):
        return self.username
