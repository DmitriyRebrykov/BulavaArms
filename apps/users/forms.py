from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'email@example.com'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': "Ім'я"
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Прізвище'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': "Ім'я користувача"
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Підтвердіть пароль'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Користувач з таким email вже існує')
        return email


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': "Ім'я користувача або Email"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Пароль'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        })
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'avatar', 'first_name', 'last_name', 'email',
            'phone', 'date_of_birth', 'address', 'city', 'postal_code'
        )
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': "Ім'я"
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Прізвище'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+380501234567'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Вулиця, будинок, квартира',
                'rows': 3
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Місто'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '01001'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-input-file',
                'accept': 'image/*'
            })
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Користувач з таким email вже існує')
        return email


class AvatarUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('avatar',)
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-input-file',
                'accept': 'image/*',
                'hx-post': '',
                'hx-trigger': 'change',
                'hx-target': '#avatar-preview',
                'hx-swap': 'outerHTML'
            })
        }