from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import check_password

from scraping.models import City, Language

User = get_user_model()


class UserLoginForm(forms.Form):
    email = forms.EmailField(max_length=100, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            qs = User.objects.filter(email=email)
            if not qs.exists():
                raise forms.ValidationError('There is no such user')
            if not check_password(password, qs[0].password):
                raise forms.ValidationError('Wrong password')
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError('User is deactivated')
        return super(UserLoginForm, self).clean(*args, **kwargs)


class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(label='Введите email', max_length=100,
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Введите пароль', max_length=100,
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Повторите пароль', max_length=100,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['email', ]

    def clean_password2(self):
        data = self.cleaned_data
        if data['password'] != data['password2']:
            raise forms.ValidationError('Пароли не совпадают')
        return data['password2']


class UserUpdateForm(forms.ModelForm):
    city = forms.ModelChoiceField(queryset=City.objects.all(), to_field_name='slug', required=True,
                                  widget=forms.Select(attrs={'class': 'form-control'}), label='Город')
    language = forms.ModelChoiceField(queryset=Language.objects.all(), to_field_name='slug', required=True,
                                      widget=forms.Select(attrs={'class': 'form-control'}), label='Специальность')
    send_email = forms.BooleanField(required=False, widget=forms.CheckboxInput, label='Получать рассылку?')

    class Meta:
        model = User
        fields = ['city', 'language', 'send_email']


class ContactForm(forms.Form):
    city = forms.CharField(required=True, max_length=100,
                           widget=forms.TextInput(attrs={'class': 'form-control'}), label='Город')
    language = forms.CharField(required=True, max_length=100,
                               widget=forms.TextInput(attrs={'class': 'form-control'}), label='Специальность')
    email = forms.EmailField(required=True, label='Введите email', max_length=100,
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['city', 'language', 'send_email']
