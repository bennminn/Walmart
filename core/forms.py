from django import forms
from .models import Profile
from django.core.exceptions import ValidationError
from django.forms import Form
# class DateInput(forms.DateInput):
#     input_type = 'date'
class LoginForm(Form):
    username = forms.CharField(widget=forms.TextInput(), label="Usuario")
    password = forms.CharField(widget=forms.PasswordInput(), label="Contraseña")
    class Meta:
        fields = ['username', 'password']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        # widgets = {
        #     'date': DateInput()
        # }
        exclude = ['present', 'updated', 'date']  # Excluye campos que no deseas mostrar en el formulario

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if not rut or rut <= 0:
            raise ValidationError('El RUT debe ser un número positivo.')
        if len(str(rut)) > 9:
            raise ValidationError('El RUT no puede tener más de 8 dígitos.')
        return rut
