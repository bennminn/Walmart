from django.shortcuts import render, HttpResponse, redirect
from .models import *
from .forms import *
import face_recognition
import numpy as np
from django.db.models import Q
import os
from django.http import JsonResponse
import base64
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from PIL import Image
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.utils import timezone
import logging
# def find_user_view(request):
#     if is_ajax(request):
#         photo = request.POST.get('photo')
#         if not photo.startswith('data:image/'):
#             print("Invalid image format")
#             return JsonResponse({'success': False, 'error': 'Invalid image format'})

#         _, str_img = photo.split(';base64')

#         try:
#             decoded_file = base64.b64decode(str_img)
#             print(f"Decoded file: {decoded_file[:100]}")  # Muestra los primeros 100 bytes del archivo

#             x = Log()
#             x.photo.save('upload.png', ContentFile(decoded_file))
#             x.save()

#             print(f"Saved image path: {x.photo.path}")  # Verifica la ruta de la imagen guardada

#             # Verifica que la imagen sea válida antes de clasificarla
#             try:
#                 with Image.open(x.photo.path) as img:
#                     img.verify()  # Verifica que el archivo sea una imagen válida
#                     print(f"Image verified successfully: {x.photo.path}")
#             except Exception as e:
#                 print(f"Invalid image file: {e}")
#                 return JsonResponse({'success': False, 'error': 'Invalid image file'})

#             res = classify_face(x.photo.path)
#             if res:
#                 user_exists = User.objects.filter(username=res).exists()
#                 if user_exists:
#                     user = User.objects.get(username=res)
#                     profile = Profile.objects.get(user=user)
#                     x.profile = profile
#                     x.save()

#                     login(request, user)
#                     return JsonResponse({'success': True})
#             return JsonResponse({'success': False})
#         except Exception as e:
#             print(f"Error processing image: {e}")
#             return JsonResponse({'success': False, 'error': str(e)})

last_face = 'no_face'
current_path = os.path.dirname(__file__)
sound_folder = os.path.join(current_path, 'sound/')
face_list_file = os.path.join(current_path, 'face_list.txt')
sound = os.path.join(sound_folder, 'beep.wav')

logger = logging.getLogger('face_attendance')
logger.debug('This is a test debug message')
logger.info('This is a test info message')
logger.warn('This is a test warn message')

def login_succes(request):
    data = {"mesg": "", "form": LoginForm()}
    username = request.GET.get('username', '')
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid:
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, "Inició sesión correctamente :)")
                    return redirect(to='index')
                else:
                    data["mesg"] = "¡Nombre de usuario o contraseña no son correctos!"
            else:
                data["mesg"] = "¡Nombre de usuario o contraseña no son correctos!"
    return render(request, 'core/login.html', {'username': username})

def logout_view(request):
    logout(request)
    return redirect('login')

def index(request):
    scanned = LastFace.objects.all().order_by('-date')
    present = Profile.objects.filter(present=True).order_by('-updated')
    absent = Profile.objects.filter(present=False)
    history = StatusChangeHistory.objects.all().order_by('-date')  # Historial de cambios

    context = {
        'scanned': scanned,
        'present': present,
        'absent': absent,
        'history': history  # Agregar historial al contexto
    }
    return render(request, 'core/index.html', context)


def ajax(request):
    last_face = LastFace.objects.last()
    context = {
        'last_face': last_face
    }
    return render(request, 'core/ajax.html', context)


def scan(request):
    if request.method == 'POST':
        logger.warn(f"Inspecting POST request: {type(request.POST)}")
        photo = request.POST.get('photo')
        if not photo.startswith('data:image/'):
            msg = 'Formato de imagen no válido'
            logger.warn(msg)
            return JsonResponse({'success': False, 'error': msg})

        _, str_img = photo.split(';base64')

        try:
            decoded_file = base64.b64decode(str_img)
            logger.warn("Image decoded successfully")

            # Guardar la imagen en la carpeta media
            temp_image_path = os.path.join('media', 'temp_image.png')
            with open(temp_image_path, 'wb') as f:
                f.write(decoded_file)
            logger.warn("Image saved to media folder")

            # Cargar la imagen y realizar el reconocimiento facial
            image = face_recognition.load_image_file(temp_image_path)
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)

            known_face_encodings = []
            known_face_names = []

            # Cargar perfiles conocidos
            profiles = Profile.objects.all()
            for profile in profiles:
                person = profile.image
                image_of_person = face_recognition.load_image_file(f'media/{person}')
                person_face_encoding = face_recognition.face_encodings(image_of_person)
                if person_face_encoding:
                    known_face_encodings.append(person_face_encoding[0])
                    known_face_names.append(profile.first_name + " " + profile.last_name)
                else:
                    logger.warn(f"No face encoding found for profile: {profile.id}")
            logger.warn(f"Known face names: {known_face_names}")

            face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "No coincide"

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches and matches[best_match_index]:
                    name = known_face_names[best_match_index]

                    # Buscar el perfil correspondiente
                    profile = Profile.objects.get(
                        first_name=name.split()[0], last_name=name.split()[1]
                    )

                    # Cambiar el status basado en el último viaje
                    previous_status = profile.status
                    if previous_status == 'Zona Cero':
                        profile.status = 'RM'
                    else:
                        profile.status = 'Zona Cero'

                    # Guardar el historial de cambios
                    StatusChangeHistory.objects.create(
                        profile=profile,
                        previous_status=previous_status,
                        new_status=profile.status
                    )

                    # Actualizar el estado del perfil
                    profile.present = True
                    profile.save()

                    # Crear un registro en LastFace
                    LastFace.objects.create(
                        profile=profile,
                        last_face=name,
                        date=timezone.now()
                    )

                    return JsonResponse({'success': True, 'profile': {
                        'rut': profile.rut,
                        'first_name': profile.first_name,
                        'last_name': profile.last_name,
                        'email': profile.email,
                        'phone': profile.phone,
                        'transportista': profile.Transportista,
                        'image_url': profile.image.url,
                        'status': profile.status
                    }})

            return JsonResponse({'success': False, 'error': 'No se detectaron coincidencias.'})

        except Exception as e:
            logger.warn(f"Unexpected error: {str(e)}")
            return JsonResponse({'success': False, 'error': f'Error inesperado: {str(e)}'})
    else:
        return JsonResponse({'success': False, 'error': 'Verbo no POST recibido'})



def profiles(request):
    profiles = Profile.objects.all()
    context = {
        'profiles': profiles
    }
    return render(request, 'core/profiles.html', context)


def details(request):
    try:
        last_face = LastFace.objects.last()
        profile = Profile.objects.get(Q(image__icontains=last_face))
    except:
        last_face = None
        profile = None

    context = {
        'profile': profile,
        'last_face': last_face
    }
    return render(request, 'core/details.html', context)


def add_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'El perfil se ha guardado correctamente.')
            return redirect('profiles')  # Redirige a la lista de perfiles después de guardar
        else:
            messages.error(request, 'Hubo un error al guardar el perfil. Por favor, verifica los datos ingresados.')
    else:
        form = ProfileForm()
    
    context = {'form': form}
    return render(request, 'core/add_profile.html', context)


def edit_profile(request,id):
    profile = Profile.objects.get(id=id)
    form = ProfileForm(instance=profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST,request.FILES,instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profiles')
    context={'form':form}
    return render(request,'core/add_profile.html',context)


def delete_profile(request,id):
    logger.warn(f'deleting profile with id: {id}')
    profile = Profile.objects.get(id=id)
    profile.delete()
    logger.warn('profile succesfully deleted')
    return redirect('profiles')


def clear_history(request):
    history = LastFace.objects.all()
    history.delete()
    return redirect('index')


def reset(request):
    profiles = Profile.objects.all()
    for profile in profiles:
        if profile.present == True:
            profile.present = False
            profile.save()
        else:
            pass
    return redirect('index')
