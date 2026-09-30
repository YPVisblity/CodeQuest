from django.contrib import admin
from .models import ShopItem, UserItem, UserProfile, AiChatUsage, Announcement


@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "description")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "points", "avatar_choice")
    list_editable = ("points",)
    search_fields = ("user__username", "user__email")
    list_select_related = ("user",)
    ordering = ("user__username",)


admin.site.register(UserItem)


@admin.register(AiChatUsage)
class AiChatUsageAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "count")
    list_filter = ("date",)
    search_fields = ("user__username",)
    list_select_related = ("user",)
    ordering = ("-date", "user__username")
#

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "content")
    list_editable = ("is_active",)