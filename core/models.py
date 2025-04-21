from django.db import models




types = [('Alta','Alta'),('Baja','Baja')]
class Profile(models.Model):
    rut = models.IntegerField(unique=True, default=0) 
    first_name = models.CharField(max_length=70)
    last_name = models.CharField(max_length=70)
    date = models.DateField(null=True, blank=True)
    phone = models.BigIntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    Transportista = models.CharField(max_length=200)
    CodTransportista = models.IntegerField(default=0, null=True, blank=True)
    # status = prioridad de zona cero.
    status = models.CharField(choices=types,max_length=20,null=True,blank=False,default='Baja')
    # presente = escaeneado con autenticación exitosa
    present = models.BooleanField(default=False)
    # con ruta asignada
    assigned = models.BooleanField(default=False)
    image = models.ImageField()
    # fecha del ultimo cambio hecho al perfil
    updated = models.DateTimeField(auto_now=True)
    # tractocamión
    Patente = models.CharField(max_length=6, default='')
    # es un recurso activo?
    active = models.BooleanField(default=True)
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

# availability being the combined state of present and assigned.
class AvailabilitySnapshotHistory(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='availability_snapshots')
    present_snapshot = models.BooleanField(default=False)
    assigned_snapshot = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=False)

    def __str__(self):
        return f"{self.profile.first_name} {self.profile.last_name}: {self.previous_status} -> {self.new_status}"