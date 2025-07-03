from django.contrib import admin
from .models import *

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['rut', 'first_name', 'last_name', 'Transportista', 'status', 'present', 'updated']
    list_filter = ['status', 'present', 'updated']
    search_fields = ['rut', 'first_name', 'last_name', 'Transportista']
    ordering = ['-updated']

@admin.register(LastFace)
class LastFaceAdmin(admin.ModelAdmin):
    list_display = ['profile', 'last_face', 'date']
    list_filter = ['date']
    ordering = ['-date']

@admin.register(StatusChangeHistory)
class StatusChangeHistoryAdmin(admin.ModelAdmin):
    list_display = ['profile', 'previous_status', 'new_status', 'date']
    list_filter = ['previous_status', 'new_status', 'date']
    ordering = ['-date']

@admin.register(SoapApiLog)
class SoapApiLogAdmin(admin.ModelAdmin):
    list_display = ['fecha_llamada', 'nom_conductor', 'rut_conductor', 'estado', 'http_status', 'cod_site']
    list_filter = ['estado', 'http_status', 'fecha_llamada', 'cod_site']
    search_fields = ['nom_conductor', 'rut_conductor', 'nom_transporte']
    ordering = ['-fecha_llamada']
    readonly_fields = ['fecha_llamada']
    
    fieldsets = (
        ('Información del Conductor', {
            'fields': ('profile', 'nom_conductor', 'rut_conductor')
        }),
        ('Datos de Transporte', {
            'fields': ('tracto', 'nom_transporte', 'rut_transporte')
        }),
        ('Parámetros de la Llamada', {
            'fields': ('fh_ingreso', 'cod_site')
        }),
        ('Resultado', {
            'fields': ('estado', 'http_status', 'respuesta_api', 'error_mensaje')
        }),
        ('Metadatos', {
            'fields': ('fecha_llamada',)
        }),
    )