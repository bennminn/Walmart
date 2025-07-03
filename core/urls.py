from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_succes, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('ajax/', views.ajax, name='ajax'),
    path('scan/', views.scan, name='scan'),
    path('profiles/', views.profiles, name='profiles'),
    path('details/', views.details, name='details'),

    path('add_profile/', views.add_profile, name='add_profile'),
    path('edit_profile/<int:id>/', views.edit_profile, name='edit_profile'),
    path('delete_profile/<int:id>/', views.delete_profile, name='delete_profile'),

    path('clear_history/', views.clear_history, name='clear_history'),
    path('reset/', views.reset, name='reset'),

    path('profile/<int:profile_id>/details/', views.profile_details, name='profile_details'),
    path('profile_rut_to_id/<int:rut>/', views.profile_rut_to_id, name='profile_rut_to_id'),
    
    # Nueva URL para logs de API SOAP
    
    path('soap-logs/', views.soap_logs, name='soap_logs'),
]
