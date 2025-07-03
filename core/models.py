from django.db import models
import base64

types = [('Zona Cero','Zona Cero'),('RM','RM')]
class Profile(models.Model):
    rut = models.IntegerField(unique=True, default=0) 
    first_name = models.CharField(max_length=70)
    last_name = models.CharField(max_length=70)
    date = models.DateField(null=True, blank=True)
    phone = models.BigIntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    Transportista = models.CharField(max_length=200)
    CodTransportista = models.IntegerField(default=0, null=True, blank=True)
    status = models.CharField(choices=types,max_length=20,null=True,blank=False,default='RM')
    present = models.BooleanField(default=False)
    image = models.ImageField()
    image_base64 = models.TextField(null=True, blank=True)  # Almacena la imagen en formato base64
    updated = models.DateTimeField(auto_now=True)
    Patente = models.CharField(max_length=6, default='HHMM77')

    def save(self, *args, **kwargs):
        # Elimina la lógica de conversión a base64 aquí
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name +' '+self.last_name


class LastFace(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='faces')  # Relación con Profile
    last_face = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.last_face


class StatusChangeHistory(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='status_changes')
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.first_name} {self.profile.last_name}: {self.previous_status} -> {self.new_status}"


class SoapApiLog(models.Model):
    """
    Modelo para registrar todas las llamadas a la API SOAP
    """
    ESTADO_CHOICES = [
        ('SUCCESS', 'Éxito'),
        ('FAILED', 'Fallido'),
        ('UNKNOWN', 'Desconocido'),
    ]
    
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='soap_logs')
    fh_ingreso = models.CharField(max_length=20)  # Formato: "20250702 14:30:00"
    cod_site = models.CharField(max_length=10)
    rut_conductor = models.CharField(max_length=20)
    nom_conductor = models.CharField(max_length=200)
    tracto = models.CharField(max_length=20, blank=True)
    rut_transporte = models.CharField(max_length=20, blank=True)
    nom_transporte = models.CharField(max_length=200, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES)
    respuesta_api = models.TextField()  # Respuesta completa de la API
    error_mensaje = models.TextField(blank=True, null=True)  # Mensaje de error si aplica
    http_status = models.IntegerField(null=True, blank=True)  # Código HTTP de respuesta
    fecha_llamada = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_llamada']
        verbose_name = 'Registro API SOAP'
        verbose_name_plural = 'Registros API SOAP'
    
    def __str__(self):
        return f"{self.nom_conductor} - {self.estado} ({self.fecha_llamada.strftime('%Y-%m-%d %H:%M')})"