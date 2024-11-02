from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin
from .models import Article, ArticleMedia, Tags

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_filter = ['author']

class ArticleMediaAdmin(admin.ModelAdmin):
    list_display = ('image','type','get_article_link', 'edit_link')
    list_filter = ['article__title']

    def get_article_link(self, obj):
        url = reverse('admin:blog_article_change', args=[obj.article.id])
        return format_html(f'<a href="{url}">{obj.article.title}</a>')

    get_article_link.short_description = 'Article'

    def edit_link(self, obj):
        url = reverse('admin:blog_articlemedia_change', args=[obj.id])
        return format_html(f'<a href="{url}">&#128393;Edit</a>')

    edit_link.short_description = 'Edit'

admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleMedia, ArticleMediaAdmin)
admin.site.register(Tags)