from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserForm(UserCreationForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    middle_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(required=True, 
                               widget=forms.TextInput(
                                    attrs={'class': "form-control",
                                           'hx-post': "/blog/check_username/", #Not the best way to do this, should update this
                                           'hx-target': "#username-check",
                                           'hx-trigger': 'keyup'}), 
                                    help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.")
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', "placeholder": "user@example.com"}))
    profile_picture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control',
                                                                                              'onchange': 'previewProfilePicture(this)'}))
    about = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Tell us about yourself....'}),
                            help_text = "Optional. Maximum - 250 words")

    class Meta:
        model = User
        fields = ('first_name','middle_name','last_name','username','email','password1','password2','about','profile_picture')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control mb-2'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control mb-2'})