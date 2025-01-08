from django.contrib import admin
from .models import Author, Post, Tag

# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'author',)
    list_filter = ('date', 'author', 'tags',)
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Author)
admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
