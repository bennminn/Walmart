from django.db import models




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
    updated = models.DateTimeField(auto_now=True)
    Patente = models.CharField(max_length=6, default='')
    def __str__(self):
        return self.first_name +' '+self.last_name


class LastFace(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='faces')  # Relación con Profile
    last_face = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.last_face

