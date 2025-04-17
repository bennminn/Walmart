from django import forms
from .models import Profile
from django.core.exceptions import ValidationError
from django.forms import Form
import base64
import logging

logger = logging.getLogger('face_attendance')


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
        logger.warn("Profile Form validando rut")
        rut = self.cleaned_data.get('rut')
        if not rut or rut <= 0:
            msg = "El RUT debe ser un número positivo."
            logger.warn(msg)
            raise ValidationError(msg)
        if len(str(rut)) > 9:
            msg = 'El RUT no puede tener más de 9 dígitos contando el digito verificador.'
            logger.warn(msg)
            raise ValidationError(msg)
        return rut

    def save(self, commit=True):
        logger.warn("Generando instancia de ProfileForm sin imagen base64")
        instance = super(ProfileForm, self).save(commit=False)
        # Procesar la imagen y convertirla a base64
        if self.cleaned_data.get('image'):
            logger.warn("Procesando imagen a base 64")
            try:
                image_file = self.cleaned_data['image']
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                instance.image_base64 = encoded_string
            except Exception as e:
                msg = f"Error al convertir la imagen a base64: {e}"
                logger.warn(msg)
                raise ValidationError(msg)
        if commit:
            logger.warn("Intentando guardar instancia final de profile form")
            try:
                instance.save()
            except Exception as e:
                msg = f"Error al intentar guardar la instancia final: {e}"
                logger.warn(msg)
                raise ValidationError(msg)
        return instance
