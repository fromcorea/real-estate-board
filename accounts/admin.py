from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'name', 'email', 'phone', 'is_agent', 'is_active', 'date_joined']
    list_filter = ['is_agent', 'is_active', 'is_staff']
    search_fields = ['username', 'name', 'email', 'phone']
    list_editable = ['is_active']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('name', 'phone', 'profile_image', 'is_agent', 'business_number')}),
    )
