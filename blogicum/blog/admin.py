from django.contrib import admin

from .models import Category, Comment, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'is_published',
        'created_at',
        'pub_date',
    )
    list_editable = (
        'is_published',
        'pub_date'
    )
    search_fields = ('title',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'created_at',
    )


admin.site.register(Category)
admin.site.register(Location)
