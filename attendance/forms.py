from django import forms
from .models import Attendance

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['date', 'clock_in_time', 'clock_out_time', 'leave_type', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'clock_in_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'clock_out_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }