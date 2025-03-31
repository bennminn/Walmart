from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ajax/', views.ajax, name='ajax'),
    path('scan/', views.scan, name='scan'),
    path('profiles/', views.profiles, name='profiles'),
    path('details/', views.details, name='details'),

    path('add_profile/', views.add_profile, name='add_profile'),
    path('edit_profile/<int:id>/', views.edit_profile, name='edit_profile'),
    path('delete_profile/<int:id>/', views.delete_profile, name='delete_profile'),

    path('clear_history/', views.clear_history, name='clear_history'),
    path('reset/', views.reset, name='reset'),
    path('driver_to_trip/', views.driver_to_trip, name='driver_to_trip'),
]
