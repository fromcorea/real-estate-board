from django import forms
from .models import Property, PropertyImage, Report, BoardPost


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'property_type', 'trade_type', 'price', 'deposit', 'monthly_rent',
            'address', 'address_detail', 'latitude', 'longitude',
            'area', 'description',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10, 'id': 'id_description'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

    def clean(self):
        cleaned = super().clean()
        trade_type = cleaned.get('trade_type')
        if trade_type == 'monthly':
            if not cleaned.get('deposit'):
                self.add_error('deposit', '월세 거래는 보증금을 입력해야 합니다.')
            if not cleaned.get('monthly_rent'):
                self.add_error('monthly_rent', '월세 거래는 월세를 입력해야 합니다.')
        return cleaned


class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image']


PropertyImageFormSet = forms.inlineformset_factory(
    Property, PropertyImage,
    form=PropertyImageForm,
    extra=5,
    max_num=10,
    can_delete=True,
)


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': '신고 사유를 자세히 적어주세요.'}),
        }


class BoardPostForm(forms.ModelForm):
    raw_password = forms.CharField(
        label='비밀번호', max_length=30, required=False,
        widget=forms.PasswordInput(attrs={'placeholder': '수정/삭제 시 필요합니다'}),
    )

    class Meta:
        model = BoardPost
        fields = ['category', 'writer_name', 'title', 'content', 'file1']
        widgets = {
            'content': forms.Textarea(attrs={'id': 'id_board_content'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user and user.is_authenticated:
            self.fields['writer_name'].required = False
            self.fields['writer_name'].widget = forms.HiddenInput()
            self.fields.pop('raw_password', None)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and self.user.is_authenticated:
            instance.author = self.user
            instance.writer_name = self.user.name or self.user.username
            instance.password = ''
        else:
            raw_pw = self.cleaned_data.get('raw_password', '')
            if raw_pw:
                instance.set_password(raw_pw)
        if commit:
            instance.save()
        return instance


class BoardPasswordForm(forms.Form):
    password = forms.CharField(
        label='비밀번호', max_length=30,
        widget=forms.PasswordInput(attrs={'placeholder': '게시글 비밀번호를 입력하세요'}),
    )
