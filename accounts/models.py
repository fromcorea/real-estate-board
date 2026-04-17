from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    name = models.CharField('이름', max_length=20, blank=True)
    phone = models.CharField('전화번호', max_length=20, blank=True)
    profile_image = models.ImageField('프로필 사진', upload_to='profiles/', blank=True)
    is_agent = models.BooleanField('공인중개사 여부', default=False)
    business_number = models.CharField('사업자등록번호', max_length=20, blank=True)

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자'

    def __str__(self):
        return self.name or self.username
