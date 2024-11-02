from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from blog.utils import PathAndRename, validate_image_size, validate_word_count # I messed up, should have put word count into authentication utils
from django.core.validators import FileExtensionValidator
import os

path_and_rename = PathAndRename("profile")

class User(AbstractUser):
    email = models.EmailField(unique=True)
    middle_name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_picture = models.ImageField(upload_to=path_and_rename, height_field=None, width_field=None, max_length=None,
                              validators=[FileExtensionValidator(allowed_extensions=['png','jpeg','jpg']),
                                          validate_image_size],default=None)
    about = models.TextField(default="No details available for this user", blank=True, validators=[validate_word_count]) #Set to 250 words
    
    def __str__(self):
        return f"{self.username}"
    
    def delete(self, *args, **kwargs):
        if self.profile_picture is not None and hasattr(self.profile_picture,'path') and os.path.exists(self.profile_picture.path):
            os.remove(self.profile_picture.path)

        super().delete(*args, **kwargs)

class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_expired(self):
        expiration_time = 3600 # 1 hour
        return timezone.now().timestamp() > self.created_at.timestamp() + expiration_time 