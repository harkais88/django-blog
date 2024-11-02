from django import forms
from .models import Article, ArticleMedia
from tinymce.widgets import TinyMCE

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title','tags','content')
        widgets = {
            'content': TinyMCE(attrs={'cols': 80, 'rows': 30})
        }

class ArticleMediaForm(forms.ModelForm):
    class Meta:
        model = ArticleMedia
        fields = ('image',)