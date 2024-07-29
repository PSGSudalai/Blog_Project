from django import forms
from .models import Blogs, Tag, Comments
from django.contrib.auth.models import User

class BlogForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Blogs
        fields = ['blog_title', 'blog_description', 'tags','thumbnail']

class CommentForm(forms.ModelForm):
    # user = forms.ModelChoiceField(
    #     queryset=User.objects.all(),
    #     widget=forms.HiddenInput(),
    # )

    class Meta:
        model = Comments
        # fields = ['user', 'text']
        fields = ['text']

class TagForm(forms.ModelForm):
    class Meta:
        model= Tag
        fields = '__all__'
