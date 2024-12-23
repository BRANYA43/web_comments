from django.contrib import admin  # NOQA
from django.contrib.auth import get_user_model

from comments.admin import CommentInline

GeneralUser = get_user_model()


@admin.register(GeneralUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_active', 'is_staff', 'last_login', 'joined')
    fieldsets = (
        ('General Info', {'fields': ('email', 'username', 'is_active')}),
        ('Permissions', {'fields': ('is_staff', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'joined')}),
    )
    readonly_fields = ('last_login', 'joined')
    filter_horizontal = ('user_permissions', 'groups')
    inlines = (CommentInline,)
