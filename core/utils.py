from django.http import JsonResponse
import random
from datetime import timedelta, datetime, timezone
from core.models import Profile, AvailabilitySnapshotHistory

import logging

logger = logging.getLogger('face_attendance')

def simulate_monthly_activity():
    profiles = Profile.objects.all()
    start_date = datetime.now(timezone.utc) - timedelta(hours=4)
    
    # Clear previous incorrect data
    AvailabilitySnapshotHistory.objects.all().delete()
    
    for day in range(30):
        current_date = start_date + timedelta(days=day)
        logger.warn(f"start date {start_date} became current date {current_date}")
        for profile in profiles:
            # Start of the day: profile is not present and not assigned
            start_time = current_date.replace(hour=0, minute=0, second=0)
            logger.warn(f"day begins time {start_time}")
            profile.present = False
            profile.assigned = False
            profile.save()
            
            AvailabilitySnapshotHistory.objects.create(
                profile=profile,
                present_snapshot=profile.present,
                assigned_snapshot=profile.assigned,
                date=start_time
            )
            
            # Profile becomes present
            arrival_time = start_time + timedelta(hours=random.randint(6, 9))  # Random arrival time between 6 AM and 9 AM
            logger.warn(f"driver arrival time {arrival_time}")
            profile.present = True
            profile.assigned = False
            profile.save()
            
            AvailabilitySnapshotHistory.objects.create(
                profile=profile,
                present_snapshot=profile.present,
                assigned_snapshot=profile.assigned,
                date=arrival_time
            )
            
            # Simulate trips throughout the day
            num_trips = random.randint(1, 5)  # Random number of trips
            for _ in range(num_trips):
                trip_start_time = arrival_time + timedelta(hours=random.randint(1, 3))  # Random trip start time
                trip_end_time = trip_start_time + timedelta(hours=random.randint(1, 2))  # Random trip duration
                logger.warn(f"trip start  time {trip_start_time}")
                logger.warn(f"trip end time {trip_end_time}")
                
                # Profile is assigned and then unassigned
                profile.assigned = True
                profile.save()
                
                AvailabilitySnapshotHistory.objects.create(
                    profile=profile,
                    present_snapshot=profile.present,
                    assigned_snapshot=profile.assigned,
                    date=trip_start_time
                )
                
                profile.assigned = False
                profile.save()
                
                AvailabilitySnapshotHistory.objects.create(
                    profile=profile,
                    present_snapshot=profile.present,
                    assigned_snapshot=profile.assigned,
                    date=trip_end_time
                )
            
            # End of the day: profile is not present and not assigned
            end_time = start_time + timedelta(hours=random.randint(17, 20))  # Random end time between 5 PM and 8 PM
            logger.warn(f"day end time {end_time}\n")
            profile.present = False
            profile.assigned = False
            profile.save()
            
            AvailabilitySnapshotHistory.objects.create(
                profile=profile,
                present_snapshot=profile.present,
                assigned_snapshot=profile.assigned,
                date=end_time
            )



def barebones_scan(request):
    if request.method == 'POST':
        profile_id = request.POST.get('profile_id')
        try:
            profile = Profile.objects.get(id=profile_id)
            profile.present = True
            profile.save()
            
            AvailabilitySnapshotHistory.objects.create(
                profile=profile,
                present_snapshot=profile.present,
                assigned_snapshot=profile.assigned,
            )
            
            return JsonResponse({'success': True, 'profile': {
                'rut': profile.rut,
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'email': profile.email,
                'phone': profile.phone,
                'transportista': profile.Transportista,
                'status': profile.status
            }})
        except Profile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Profile not found'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})