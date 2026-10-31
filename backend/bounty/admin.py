from django.contrib import admin


from .models import HuntLog, WantedCriminal


class HuntLogInline(admin.TabularInline):
    model = HuntLog
    extra = 0
    readonly_fields = ["created_at"]


@admin.register(WantedCriminal)
class WantedCriminalAdmin(admin.ModelAdmin):
    list_display = ["id", "nickname", "name", "reward", "difficulty", "armed", "has_crew", "escape_master"]
    list_filter = ["armed", "has_crew", "escape_master"]
    search_fields = ["nickname", "name"]
    inlines = [HuntLogInline]


@admin.register(HuntLog)
class HuntLogAdmin(admin.ModelAdmin):
    list_display = ["id", "criminal", "success", "created_at"]
    list_filter = ["success"]
    readonly_fields = ["created_at"]