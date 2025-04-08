from django import forms
from .models import Profile
from django.core.exceptions import ValidationError
from django.forms import Form
import base64

class LoginForm(Form):
    username = forms.CharField(widget=forms.TextInput(), label="Usuario")
    password = forms.CharField(widget=forms.PasswordInput(), label="Contraseña")
    class Meta:
        fields = ['username', 'password']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['present', 'updated', 'date', 'image_base64']  # Excluye campos que no deseas mostrar en el formulario

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if not rut or rut <= 0:
            raise ValidationError('El RUT debe ser un número positivo.')
        if len(str(rut)) > 8:
            raise ValidationError('El RUT no puede tener más de 8 dígitos.')
        return rut

    def save(self, commit=True):
        instance = super(ProfileForm, self).save(commit=False)
        # Procesar la imagen y convertirla a base64
        if self.cleaned_data.get('image'):
            try:
                image_file = self.cleaned_data['image']
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                instance.image_base64 = encoded_string
            except Exception as e:
                raise ValidationError(f"Error al convertir la imagen a base64: {e}")
        if commit:
            instance.save()
        return instance
