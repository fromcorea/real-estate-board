from django import forms
from .models import Property, PropertyImage, Report


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'property_type', 'trade_type', 'price', 'deposit', 'monthly_rent',
            'address', 'address_detail', 'latitude', 'longitude',
            'area', 'rooms', 'bathrooms', 'floor', 'direction', 'heating',
            'parking', 'maintenance_fee', 'available_date', 'description',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'available_date': forms.DateInput(attrs={'type': 'date'}),
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
