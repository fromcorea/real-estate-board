import uuid

from django.conf import settings
from django.db import models


def property_image_path(instance, filename):
    ext = filename.rsplit('.', 1)[-1] if '.' in filename else 'jpg'
    return f'properties/{uuid.uuid4().hex}.{ext}'


class Property(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('apartment', '아파트'),
        ('house', '단독/다가구'),
        ('villa', '연립/빌라'),
        ('oneroom', '방한칸'),
        ('office', '사무실/오피스텔'),
        ('restaurant', '요식업/영업점'),
        ('store', '상가점포/빌딩'),
        ('land', '대지/임야'),
        ('factory', '공장/창고/기타'),
    ]
    TRADE_TYPE_CHOICES = [
        ('sale', '매매'),
        ('jeonse', '전세'),
        ('monthly', '월세'),
    ]
    STATUS_CHOICES = [
        ('pending', '대기중'),
        ('approved', '승인'),
        ('rejected', '반려'),
        ('completed', '거래완료'),
    ]
    DIRECTION_CHOICES = [
        ('east', '동향'), ('west', '서향'), ('south', '남향'), ('north', '북향'),
        ('southeast', '남동향'), ('southwest', '남서향'),
        ('northeast', '북동향'), ('northwest', '북서향'),
    ]
    HEATING_CHOICES = [
        ('individual', '개별난방'),
        ('central', '중앙난방'),
        ('district', '지역난방'),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='properties', verbose_name='등록자',
                               null=True, blank=True)
    title = models.CharField('제목', max_length=100)
    description = models.TextField('매물 설명')
    property_type = models.CharField('매물유형', max_length=20, choices=PROPERTY_TYPE_CHOICES)
    trade_type = models.CharField('거래유형', max_length=10, choices=TRADE_TYPE_CHOICES)
    price = models.PositiveIntegerField('매매가/전세금(만원)')
    deposit = models.PositiveIntegerField('보증금(만원)', null=True, blank=True)
    monthly_rent = models.PositiveIntegerField('월세(만원)', null=True, blank=True)
    area = models.DecimalField('면적(m2)', max_digits=10, decimal_places=2)
    address = models.CharField('주소', max_length=200)
    address_detail = models.CharField('상세주소', max_length=100, blank=True)
    latitude = models.DecimalField('위도', max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField('경도', max_digits=10, decimal_places=7, null=True, blank=True)
    floor = models.PositiveSmallIntegerField('층수', null=True, blank=True)
    rooms = models.PositiveSmallIntegerField('방 수', default=1)
    bathrooms = models.PositiveSmallIntegerField('화장실 수', default=1)
    direction = models.CharField('방향', max_length=10, choices=DIRECTION_CHOICES, blank=True)
    heating = models.CharField('난방', max_length=20, choices=HEATING_CHOICES, blank=True)
    parking = models.BooleanField('주차 가능', null=True, blank=True)
    maintenance_fee = models.PositiveIntegerField('관리비(만원)', null=True, blank=True)
    available_date = models.DateField('입주가능일', null=True, blank=True)
    status = models.CharField('상태', max_length=20, choices=STATUS_CHOICES, default='approved')
    is_available = models.BooleanField('거래 가능', default=True)
    view_count = models.PositiveIntegerField('조회수', default=0)
    created_at = models.DateTimeField('등록일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)

    class Meta:
        verbose_name = '매물'
        verbose_name_plural = '매물'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property_type', 'trade_type']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.title

    @property
    def price_display(self):
        if self.trade_type == 'monthly':
            return f"월세 {self.deposit:,}/{self.monthly_rent:,}만"
        elif self.trade_type == 'jeonse':
            return f"전세 {self.price:,}만"
        else:
            if self.price >= 10000:
                억 = self.price // 10000
                만 = self.price % 10000
                if 만:
                    return f"매매 {억}억 {만:,}만"
                return f"매매 {억}억"
            return f"매매 {self.price:,}만"

    @property
    def area_pyeong(self):
        return round(float(self.area) * 0.3025, 1)

    @property
    def thumbnail(self):
        img = self.images.filter(is_thumbnail=True).first()
        if not img:
            img = self.images.first()
        return img


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE,
                                 related_name='images', verbose_name='매물')
    image = models.ImageField('이미지', upload_to=property_image_path)
    is_thumbnail = models.BooleanField('대표이미지', default=False)
    order = models.PositiveSmallIntegerField('순서', default=0)
    created_at = models.DateTimeField('등록일', auto_now_add=True)

    class Meta:
        verbose_name = '매물 이미지'
        verbose_name_plural = '매물 이미지'
        ordering = ['order']

    def __str__(self):
        return f"{self.property.title} - 이미지 {self.order}"


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='bookmarks', verbose_name='사용자')
    property = models.ForeignKey(Property, on_delete=models.CASCADE,
                                 related_name='bookmarks', verbose_name='매물')
    created_at = models.DateTimeField('등록일', auto_now_add=True)

    class Meta:
        verbose_name = '북마크'
        verbose_name_plural = '북마크'
        unique_together = ('user', 'property')

    def __str__(self):
        return f"{self.user} - {self.property}"


class Report(models.Model):
    REASON_CHOICES = [
        ('fake', '허위매물'),
        ('inappropriate', '부적절한 내용'),
        ('fraud', '사기 의심'),
        ('completed', '이미 거래완료'),
        ('other', '기타'),
    ]
    STATUS_CHOICES = [
        ('pending', '대기중'),
        ('resolved', '처리완료'),
        ('dismissed', '기각'),
    ]

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='reports', verbose_name='신고자')
    property = models.ForeignKey(Property, on_delete=models.CASCADE,
                                 related_name='reports', verbose_name='매물')
    reason = models.CharField('사유', max_length=20, choices=REASON_CHOICES)
    description = models.TextField('상세 사유', blank=True)
    status = models.CharField('처리상태', max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField('관리자 메모', blank=True)
    created_at = models.DateTimeField('신고일', auto_now_add=True)
    resolved_at = models.DateTimeField('처리일', null=True, blank=True)

    class Meta:
        verbose_name = '신고'
        verbose_name_plural = '신고'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_reason_display()}] {self.property.title}"


def board_file_path(instance, filename):
    ext = filename.rsplit('.', 1)[-1] if '.' in filename else 'jpg'
    return f'board/{uuid.uuid4().hex}.{ext}'


class BoardPost(models.Model):
    CATEGORY_CHOICES = Property.PROPERTY_TYPE_CHOICES

    category = models.CharField('분류', max_length=20, choices=CATEGORY_CHOICES)
    writer_name = models.CharField('작성자', max_length=30)
    password = models.CharField('비밀번호', max_length=128)
    title = models.CharField('제목', max_length=200)
    content = models.TextField('글내용')
    file1 = models.FileField('파일첨부', upload_to=board_file_path, blank=True)
    view_count = models.PositiveIntegerField('조회수', default=0)
    created_at = models.DateTimeField('등록일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)

    class Meta:
        verbose_name = '매물 게시판'
        verbose_name_plural = '매물 게시판'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def set_password(self, raw_password):
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)


class Notice(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               verbose_name='작성자')
    title = models.CharField('제목', max_length=100)
    content = models.TextField('내용')
    is_pinned = models.BooleanField('상단 고정', default=False)
    created_at = models.DateTimeField('작성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)

    class Meta:
        verbose_name = '공지사항'
        verbose_name_plural = '공지사항'
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title
