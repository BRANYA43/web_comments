from django.contrib import admin  # NOQA

from comments.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'user', 'is_answer', 'created', 'updated')
    fieldsets = (
        ('General Info', {'fields': ('uuid', 'user', 'target')}),
        ('Content', {'fields': ('text', 'image', 'file')}),
        ('Dates', {'fields': ('created', 'updated')}),
    )
    readonly_fields = ('uuid', 'created', 'updated', 'is_answer')

    @admin.display(boolean=True)
    def is_answer(self, instance) -> bool:
        return bool(instance.target)
