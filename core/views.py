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
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.utils import timezone
import logging
import xml.etree.ElementTree as ET
import requests
from datetime import datetime, timedelta
import json

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
logger.warning('This is a test warn message')

def call_soap_api(profile):
    """
    Llama a la API SOAP con los datos del perfil encontrado
    Retorna un diccionario con el estado de la operación y guarda el registro en BD
    """
    # Variables para el log
    soap_log = None
    http_status = None
    
    try:
        # Validar que el perfil tenga los datos mínimos necesarios
        if not profile or not hasattr(profile, 'rut') or not profile.rut:
            error_msg = 'Perfil inválido o sin RUT'
            # Crear log de error de validación
            SoapApiLog.objects.create(
                profile=profile if profile else None,
                fh_ingreso='',
                cod_site='',
                rut_conductor='',
                nom_conductor='',
                tracto='',
                rut_transporte='',
                nom_transporte='',
                estado='FAILED',
                respuesta_api='',
                error_mensaje=error_msg,
                http_status=None
            )
            return {
                'success': False,
                'estado': 'FAILED',
                'error': error_msg
            }
        
        # Generar timestamp actual en formato exacto requerido: "20250623 17:00:00"
        fh = datetime.now().strftime("%Y%m%d %H:%M:%S")
        cod_site = "6009"  # Valor fijo según tu ejemplo
        
        # Datos del perfil con validaciones
        rut_conductor = str(profile.rut).strip()
        nom_conductor = f"{profile.first_name or ''} {profile.last_name or ''}".strip()
        tracto = str(getattr(profile, 'Patente', '') or '').strip()
        rut_transporte = str(getattr(profile, 'CodTransportista', '') or '').strip()
        nom_transporte = str(profile.Transportista or '').strip()
        
        # Validar datos críticos
        if not rut_conductor:
            error_msg = 'RUT del conductor es requerido'
            SoapApiLog.objects.create(
                profile=profile,
                fh_ingreso=fh,
                cod_site=cod_site,
                rut_conductor=rut_conductor,
                nom_conductor=nom_conductor,
                tracto=tracto,
                rut_transporte=rut_transporte,
                nom_transporte=nom_transporte,
                estado='FAILED',
                respuesta_api='',
                error_mensaje=error_msg,
                http_status=None
            )
            return {
                'success': False,
                'estado': 'FAILED',
                'error': error_msg
            }
        
        if not nom_conductor or nom_conductor.strip() == '':
            error_msg = 'Nombre del conductor es requerido'
            SoapApiLog.objects.create(
                profile=profile,
                fh_ingreso=fh,
                cod_site=cod_site,
                rut_conductor=rut_conductor,
                nom_conductor=nom_conductor,
                tracto=tracto,
                rut_transporte=rut_transporte,
                nom_transporte=nom_transporte,
                estado='FAILED',
                respuesta_api='',
                error_mensaje=error_msg,
                http_status=None
            )
            return {
                'success': False,
                'estado': 'FAILED',
                'error': error_msg
            }
        
        soap_body = f"""
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <inserta_registro_conductor xmlns="http://tempuri.org/">
      <fh_ingreso>{fh}</fh_ingreso>
      <cod_site>{cod_site}</cod_site>
      <rut_conductor>{rut_conductor}</rut_conductor>
      <nom_conductor>{nom_conductor}</nom_conductor>
      <tracto>{tracto}</tracto>
      <rut_transporte>{rut_transporte}</rut_transporte>
      <nom_transporte>{nom_transporte}</nom_transporte>
    </inserta_registro_conductor>
  </soap:Body>
</soap:Envelope>
"""
        
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://tempuri.org/inserta_registro_conductor',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Proxy-Connection': 'Keep-Alive',
            'Server': 'Microsoft-IIS/7.5'
        }
        
        url = "http://ww2.qanalytics.cl/wm_consultaviajes/qviajes.asmx"
        
        # Log de los parámetros que se enviarán
        logger.warning(f"Parámetros SOAP - fh: {fh}, cod_site: {cod_site}, rut_conductor: {rut_conductor}, nom_conductor: {nom_conductor}, tracto: {tracto}, rut_transporte: {rut_transporte}, nom_transporte: {nom_transporte}")
        logger.warning(f"Llamando a API SOAP para perfil: {nom_conductor}")
        
        response = requests.post(url, data=soap_body, headers=headers, timeout=30)
        http_status = response.status_code
        
        # Procesar la respuesta XML según el código de estado
        if response.status_code == 200:
            try:
                # Respuesta exitosa - procesar normalmente
                root = ET.fromstring(response.content)
                response_dict = {child.tag: child.text for child in root.iter()}
                response_json = json.dumps(response_dict, indent=4)
                
                json_text = response_json.replace("\\n", "").replace("\\", "")
                json_data = json.loads(json_text)
                xml_content = json_data.get("{http://tempuri.org/}inserta_registro_conductorResult", "UNKNOWN")
                
                # Determinar el estado basado en la respuesta
                estado = "SUCCESS" if xml_content and ("success" in xml_content.lower() or "ok" in xml_content.lower() or "exitoso" in xml_content.lower()) else "FAILED"
                
                logger.warning(f"API SOAP response (200): {xml_content}, Estado: {estado}")
                
                # Guardar log en base de datos
                SoapApiLog.objects.create(
                    profile=profile,
                    fh_ingreso=fh,
                    cod_site=cod_site,
                    rut_conductor=rut_conductor,
                    nom_conductor=nom_conductor,
                    tracto=tracto,
                    rut_transporte=rut_transporte,
                    nom_transporte=nom_transporte,
                    estado=estado,
                    respuesta_api=xml_content,
                    error_mensaje=None if estado == 'SUCCESS' else xml_content,
                    http_status=http_status
                )
                
                return {
                    'success': True,
                    'estado': estado,
                    'response': xml_content,
                    'data': {
                        "fh": fh,
                        "cod_site": cod_site,
                        "rut_conductor": rut_conductor,
                        "nom_conductor": nom_conductor,
                        "tracto": tracto,
                        "rut_transporte": rut_transporte,
                        "nom_transporte": nom_transporte,
                        "respuesta_api": xml_content
                    }
                }
            except (ET.ParseError, json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Error procesando respuesta XML/JSON (200): {str(e)}")
                error_msg = f'Error procesando respuesta: {str(e)}'
                
                # Guardar log de error de procesamiento
                SoapApiLog.objects.create(
                    profile=profile,
                    fh_ingreso=fh,
                    cod_site=cod_site,
                    rut_conductor=rut_conductor,
                    nom_conductor=nom_conductor,
                    tracto=tracto,
                    rut_transporte=rut_transporte,
                    nom_transporte=nom_transporte,
                    estado='FAILED',
                    respuesta_api=response.text[:1000],  # Primeros 1000 caracteres
                    error_mensaje=error_msg,
                    http_status=http_status
                )
                
                return {
                    'success': False,
                    'estado': 'FAILED',
                    'error': error_msg,
                    'raw_response': response.text[:500]  # Primeros 500 caracteres para debug
                }
                
        elif response.status_code == 500:
            try:
                # Error del servidor - extraer faultstring
                root = ET.fromstring(response.content)
                response_dict = {child.tag: child.text for child in root.iter()}
                response_json = json.dumps(response_dict, indent=4)
                
                json_text = response_json.replace("\\n", "").replace("\\", "")
                json_data = json.loads(json_text)
                xml_content = json_data.get("faultstring", "Error del servidor desconocido")
                
                logger.warning(f"API SOAP error (500): {xml_content}")
                
                # Guardar log de error del servidor
                SoapApiLog.objects.create(
                    profile=profile,
                    fh_ingreso=fh,
                    cod_site=cod_site,
                    rut_conductor=rut_conductor,
                    nom_conductor=nom_conductor,
                    tracto=tracto,
                    rut_transporte=rut_transporte,
                    nom_transporte=nom_transporte,
                    estado='FAILED',
                    respuesta_api=xml_content,
                    error_mensaje=f'Error del servidor: {xml_content}',
                    http_status=http_status
                )
                
                return {
                    'success': False,
                    'estado': 'FAILED',
                    'response': xml_content,
                    'error': f'Error del servidor: {xml_content}',
                    'data': {
                        "fh": fh,
                        "cod_site": cod_site,
                        "rut_conductor": rut_conductor,
                        "nom_conductor": nom_conductor,
                        "tracto": tracto,
                        "rut_transporte": rut_transporte,
                        "nom_transporte": nom_transporte,
                        "respuesta_api": xml_content
                    }
                }
            except (ET.ParseError, json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Error procesando respuesta de error (500): {str(e)}")
                error_msg = f'Error del servidor - No se pudo procesar: {str(e)}'
                
                # Guardar log de error de procesamiento del error 500
                SoapApiLog.objects.create(
                    profile=profile,
                    fh_ingreso=fh,
                    cod_site=cod_site,
                    rut_conductor=rut_conductor,
                    nom_conductor=nom_conductor,
                    tracto=tracto,
                    rut_transporte=rut_transporte,
                    nom_transporte=nom_transporte,
                    estado='FAILED',
                    respuesta_api=response.text[:1000],
                    error_mensaje=error_msg,
                    http_status=http_status
                )
                
                return {
                    'success': False,
                    'estado': 'FAILED',
                    'error': error_msg,
                    'raw_response': response.text[:500]
                }
        else:
            # Otros códigos de estado HTTP
            logger.warning(f"Error en API SOAP: Status {response.status_code}")
            error_msg = f'HTTP {response.status_code}: {response.text[:200]}'
            
            # Guardar log de otros errores HTTP
            SoapApiLog.objects.create(
                profile=profile,
                fh_ingreso=fh,
                cod_site=cod_site,
                rut_conductor=rut_conductor,
                nom_conductor=nom_conductor,
                tracto=tracto,
                rut_transporte=rut_transporte,
                nom_transporte=nom_transporte,
                estado='FAILED',
                respuesta_api=response.text[:1000],
                error_mensaje=error_msg,
                http_status=http_status
            )
            
            return {
                'success': False,
                'estado': 'FAILED',
                'error': error_msg
            }
            
    except requests.exceptions.Timeout:
        logger.warning("Timeout en llamada a API SOAP")
        error_msg = 'Timeout en la conexión'
        
        # Guardar log de timeout
        try:
            SoapApiLog.objects.create(
                profile=profile,
                fh_ingreso=fh if 'fh' in locals() else '',
                cod_site=cod_site if 'cod_site' in locals() else '',
                rut_conductor=rut_conductor if 'rut_conductor' in locals() else '',
                nom_conductor=nom_conductor if 'nom_conductor' in locals() else '',
                tracto=tracto if 'tracto' in locals() else '',
                rut_transporte=rut_transporte if 'rut_transporte' in locals() else '',
                nom_transporte=nom_transporte if 'nom_transporte' in locals() else '',
                estado='FAILED',
                respuesta_api='',
                error_mensaje=error_msg,
                http_status=None
            )
        except:
            pass  # Si falla el log, no interrumpir el flujo
            
        return {
            'success': False,
            'estado': 'FAILED',
            'error': error_msg
        }
    except Exception as e:
        logger.warning(f"Error inesperado en API SOAP: {str(e)}")
        error_msg = f'Error inesperado: {str(e)}'
        
        # Guardar log de error inesperado
        try:
            SoapApiLog.objects.create(
                profile=profile,
                fh_ingreso=fh if 'fh' in locals() else '',
                cod_site=cod_site if 'cod_site' in locals() else '',
                rut_conductor=rut_conductor if 'rut_conductor' in locals() else '',
                nom_conductor=nom_conductor if 'nom_conductor' in locals() else '',
                tracto=tracto if 'tracto' in locals() else '',
                rut_transporte=rut_transporte if 'rut_transporte' in locals() else '',
                nom_transporte=nom_transporte if 'nom_transporte' in locals() else '',
                estado='FAILED',
                respuesta_api='',
                error_mensaje=error_msg,
                http_status=None
            )
        except:
            pass  # Si falla el log, no interrumpir el flujo
            
        return {
            'success': False,
            'estado': 'FAILED',
            'error': error_msg
        }

def login_succes(request):
    data = {"mesg": "", "form": LoginForm()}
    username = request.GET.get('username', '')
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
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
        logger.warning(f"Inspecting POST request: {type(request.POST)}")
        photo = request.POST.get('photo')
        if not photo or not photo.startswith('data:image/'):
            msg = 'Formato de imagen no válido o imagen no proporcionada'
            logger.warning(msg)
            return JsonResponse({'success': False, 'error': msg})

        _, str_img = photo.split(';base64')

        try:
            decoded_file = base64.b64decode(str_img)
            logger.warning("Image decoded successfully")

            # Cargar la imagen directamente desde base64
            image = face_recognition.load_image_file(ContentFile(decoded_file))
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)

            known_face_encodings = []
            known_face_names = []

            # Cargar perfiles conocidos desde la base de datos
            profiles = Profile.objects.all()
            for profile in profiles:
                if profile.image_base64:
                    decoded_image = base64.b64decode(profile.image_base64)
                    image_of_person = face_recognition.load_image_file(ContentFile(decoded_image))
                    person_face_encoding = face_recognition.face_encodings(image_of_person)
                    if person_face_encoding:
                        known_face_encodings.append(person_face_encoding[0])
                        known_face_names.append(profile.first_name + " " + profile.last_name)
                    else:
                        logger.warning(f"No face encoding found for profile: {profile.id}")
            logger.warning(f"Known face names: {known_face_names}")

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
                    profile.status = 'RM' if previous_status == 'Zona Cero' else 'Zona Cero'

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

                    # Llamar a la API SOAP con los datos del perfil
                    soap_response = call_soap_api(profile)
                    logger.warning(f"SOAP API response: {soap_response}")

                    return JsonResponse({'success': True, 'profile': {
                        'id': profile.id,  # Asegúrate de incluir el ID del perfil
                        'rut': profile.rut,
                        'first_name': profile.first_name,
                        'last_name': profile.last_name,
                        'email': profile.email,
                        'phone': profile.phone,
                        'transportista': profile.Transportista,
                        'image_base64': profile.image_base64,  # Incluye la imagen base64
                        'status': profile.status,
                        'Patente': profile.Patente
                    }, 'soap_api': {
                        'estado': soap_response.get('estado', 'UNKNOWN'),
                        'success': soap_response.get('success', False),
                        'response': soap_response.get('response', ''),
                        'error': soap_response.get('error', '')
                    }})

            return JsonResponse({'success': False, 'error': 'No se detectaron coincidencias.'})

        except base64.binascii.Error as e:
            logger.warning(f"Error decoding base64 image: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Error al decodificar la imagen.'})
        except Exception as e:
            logger.warning(f"Unexpected error: {str(e)}")
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
    logger.warning(f'deleting profile with id: {id}')
    profile = Profile.objects.get(id=id)
    profile.delete()
    logger.warning('profile succesfully deleted')
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

def profile_details(request, profile_id):
    try:
        profile = Profile.objects.get(id=profile_id)
        profile_data = {
            'rut': profile.rut,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'email': profile.email,
            'phone': profile.phone,
            'transportista': profile.Transportista,
            'status': profile.status
        }
        return JsonResponse({'success': True, 'profile': profile_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error inesperado: {str(e)}'})

def profile_rut_to_id(request, rut):
    try:
        profile = Profile.objects.get(rut=rut)
        print(profile.__dict__)
        return JsonResponse({'success': True, 'profile_id': profile.id})
    except Profile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Profile not found'}, status=404)

def soap_logs(request):
    """
    Vista para mostrar el historial de llamadas a la API SOAP
    """
    logs = SoapApiLog.objects.all().order_by('-fecha_llamada')[:100]  # Últimos 100 registros
    
    context = {
        'logs': logs
    }
    return render(request, 'core/soap_logs.html', context)