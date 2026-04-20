from django.contrib import admin
from .models import Property, PropertyImage, Bookmark, Report, Notice, BoardPost


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    max_num = 10


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'property_type', 'trade_type',
                    'price', 'status', 'view_count', 'created_at']
    list_filter = ['property_type', 'trade_type', 'status', 'is_available']
    search_fields = ['title', 'address', 'author__username']
    list_editable = ['status']
    inlines = [PropertyImageInline]
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    actions = ['approve_listings', 'reject_listings']

    @admin.action(description="선택 매물 승인")
    def approve_listings(self, request, queryset):
        count = queryset.update(status='approved')
        self.message_user(request, f"{count}건 승인 완료")

    @admin.action(description="선택 매물 반려")
    def reject_listings(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f"{count}건 반려 완료")


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'property', 'created_at']
    list_filter = ['created_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['property', 'reporter', 'reason', 'status', 'created_at']
    list_filter = ['reason', 'status']
    list_editable = ['status']
    search_fields = ['property__title', 'reporter__username']
    readonly_fields = ['reporter', 'property', 'reason', 'description', 'created_at']
    actions = ['resolve_reports', 'dismiss_reports']

    @admin.action(description="선택 신고 처리완료")
    def resolve_reports(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='resolved', resolved_at=timezone.now())

    @admin.action(description="선택 신고 기각")
    def dismiss_reports(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='dismissed', resolved_at=timezone.now())


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_pinned', 'created_at']
    list_filter = ['is_pinned']
    list_editable = ['is_pinned']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(BoardPost)
class BoardPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'writer_name', 'view_count', 'created_at']
    list_filter = ['category']
    search_fields = ['title', 'writer_name', 'content']
