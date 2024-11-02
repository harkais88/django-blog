from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from authentication.models import User
from tinymce.models import HTMLField
from .utils import PathAndRename, validate_image_size
import os

class Tags(models.Model):
    name = models.CharField(max_length=50,unique=True)

    def __str__(self):
        return self.name

class Article(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = HTMLField(blank=True,null=True)
    tags = models.ManyToManyField(Tags, related_name='articles', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} posted by {self.author} on {self.created_at}"
    
    def get_image(self):
        return ArticleMedia.objects.get(article = self, type='BANNER')

path_and_rename = PathAndRename("images")

class ArticleMedia(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=path_and_rename, height_field=None, width_field=None, max_length=None,
                              validators=[FileExtensionValidator(allowed_extensions=['png','jpeg','jpg']),
                                          validate_image_size])
    
    TYPE_CHOICES = [
        ('BANNER','banner'),
        ('DETAIL','detail'),
    ]
    type = models.CharField(max_length=50,choices=TYPE_CHOICES,default='BANNER')
    filename = models.CharField(max_length=255)
    size = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.image.name}"
    
    def delete(self, *args, **kwargs):
        try:
            os.remove(self.image.path)
        except:
            pass
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.type == 'BANNER' and ArticleMedia.objects.filter(article = self.article, type = 'BANNER').exists():
            raise ValidationError('Only one banner image is allowed per article')

        super().save(*args, **kwargs)