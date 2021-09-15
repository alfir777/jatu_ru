from django import forms
from django.contrib import admin
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.utils.safestring import mark_safe

from .models import *


class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Post
        fields = '__all__'


class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    prepopulated_fields = {'slug': ('title',)}
    save_as = True
    save_on_top = True
    list_display = ('id', 'title', 'category', 'created_at', 'updated_at', 'is_published', 'get_photo')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'content')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'category', 'tags')
    readonly_fields = ('author', 'get_photo', 'views', 'created_at', 'updated_at')
    fields = ('title', 'slug', 'category', 'content', 'photo', 'get_photo', 'is_published', 'views',
              'created_at', 'updated_at', 'tags', 'author')

    def get_photo(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="50">')
        else:
            return '-'

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            obj.author = request.user
            obj.save()

    get_photo.short_description = 'Миниатюра'


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


class CommentAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('post', 'author', 'created_at')}


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Comment, CommentAdmin)
