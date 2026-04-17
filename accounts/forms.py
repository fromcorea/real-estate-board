from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    name = forms.CharField(max_length=20, label='이름')
    phone = forms.CharField(max_length=20, required=False, label='전화번호')
    is_agent = forms.BooleanField(required=False, label='공인중개사입니다')
    business_number = forms.CharField(max_length=20, required=False, label='사업자등록번호')

    class Meta:
        model = User
        fields = ('username', 'email', 'name', 'phone', 'password1', 'password2',
                  'is_agent', 'business_number')

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('is_agent') and not cleaned.get('business_number'):
            self.add_error('business_number', '공인중개사는 사업자등록번호를 입력해야 합니다.')
        return cleaned


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('name', 'email', 'phone', 'profile_image')
