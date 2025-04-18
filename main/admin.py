from django.contrib import admin
from .models import UserProfile, LoginLog


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "address", "phone_number", "latitude", "longitude"]
    search_fields = ["user__username", "user__email", "address", "phone_number"]


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "timestamp"]
    list_filter = ["action", "timestamp"]
    search_fields = ["user__username"]
    readonly_fields = ["user", "action", "timestamp"]

    def has_add_permission(self, request):
        # Disable adding login logs manually
        return False

    def has_change_permission(self, request, obj=None):
        # Disable editing login logs
        return False
