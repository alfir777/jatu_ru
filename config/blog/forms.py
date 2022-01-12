from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from blog.models import Category, Comment, Post, Tag


class BlogForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'content', 'is_published', 'category', 'tags']

    title = forms.CharField(max_length=255,
                            label='Название (проверяется на уникальность)',
                            widget=forms.TextInput(attrs={"class": "form-control"}))
    description = forms.CharField(max_length=255,
                                  label='Краткое описание (255 символов)',
                                  widget=CKEditorWidget(
                                      config_name='basic', attrs={"class": "form-control", "rows": 2, }
                                  ),
                                  )
    content = forms.CharField(label='Текст',
                              required=False,
                              widget=CKEditorWidget(
                                  config_name='custom_config', attrs={"class": "form-control", "rows": 20, }
                              ),
                              )
    is_published = forms.BooleanField(label='Опубликовано?', required=False, initial=True)
    category = forms.ModelChoiceField(empty_label='Выберите категорию',
                                      queryset=Category.objects.all(),
                                      label='Категория',
                                      widget=forms.Select(attrs={"class": "form-control"})
                                      )
    tags = forms.ModelMultipleChoiceField(required=False,
                                          queryset=Tag.objects.all(),
                                          widget=forms.CheckboxSelectMultiple,
                                          )


class ContactForm(forms.Form):
    subject = forms.CharField(label='Тема', widget=forms.TextInput(attrs={"class": "form-control"}))
    content = forms.CharField(label='Текст', widget=forms.Textarea(attrs={"class": "form-control", "rows": 5}))
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={"class": "form-control"}))
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(label='Имя пользователя',
                               widget=forms.TextInput(attrs={"class": "form-control"})
                               )
    first_name = forms.CharField(label='Имя', widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(label='Фамилия', widget=forms.TextInput(attrs={"class": "form-control"}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(label='Подтверждение пароля',
                                widget=forms.PasswordInput(attrs={"class": "form-control"})
                                )
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={"class": "form-control"}))
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class RestorePasswordForm(forms.Form):
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={"class": "form-control"}))


class UserCommentForm(forms.Form):
    form = BlogForm
    content = forms.CharField(label='Текст', widget=forms.Textarea(attrs={"class": "form-control", "rows": 5}))

    class Meta:
        model = Comment
        exclude = ('is_published',)
        widgets = {'form': forms.HiddenInput()}
        fields = ('content', 'author_id')

    def save(self, request, obj, form):
        if form.is_valid():
            obj.author = request.user
            obj.save()


# TODO Реализовать возможность добавления комментариев без авторизации
class GuestCommentForm(forms.Form):
    form = BlogForm
    content = forms.CharField(label='Текст', widget=forms.Textarea(attrs={"class": "form-control", "rows": 5}))

    class Meta:
        model = Comment
        exclude = ('is_published',)
        widgets = {'post': forms.HiddenInput}
        fields = ('content', 'author_id')

    def save(self, request, obj, form):
        if form.is_valid():
            obj.author = request.user
            obj.save()
