from django import forms
from .models import Article, ArticleMedia, Comments
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

class CommentsForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = Comments
        fields = ('content',)