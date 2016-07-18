from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION, DELETION, CHANGE
from django.utils.translation import ugettext_lazy as _

from .models import Category, CategoryIcon
from .models import Project, Data, Thumbnail, VisualizeType, Visualize


class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_type_id', 'view_action_flag',
                    'change_message', 'action_time')

    ACTION_FLAG = {
        ADDITION: _('addition'),
        DELETION: _('deletion'),
        CHANGE: _('change'),
    }

    def view_action_flag(self, obj):
        return self.ACTION_FLAG[obj.action_flag]

    view_action_flag.short_name = 'action_flag'

admin.site.register(LogEntry, LogEntryAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'code', 'created', 'modified')


class CategoryIconAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created', 'modified')
    readonly_fields = ('image_tag', )

admin.site.register(Category, CategoryAdmin)
admin.site.register(CategoryIcon, CategoryIconAdmin)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'status', 'hits',
                    'copyright', 'published', 'created', 'modified')


class DataAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'created', 'modified')


class ThumbnailAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'modified')
    readonly_fields = ('image_tag', )


class VisualizeTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'alias', 'description',
                    'created', 'modified')
    readonly_fields = ('image_tag', 'sample_image_tag', 'setting_image_tag')


class VisualizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'order', 'visualize_type',
                    'created', 'modified')


admin.site.register(Project, ProjectAdmin)
admin.site.register(Data, DataAdmin)
admin.site.register(Thumbnail, ThumbnailAdmin)
admin.site.register(VisualizeType, VisualizeTypeAdmin)
admin.site.register(Visualize, VisualizeAdmin)
