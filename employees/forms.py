from django import forms
from django.contrib.auth.forms import AuthenticationForm

class EmployeeLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='社員番号',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '社員番号を入力'})
    )
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'パスワードを入力'})
    )