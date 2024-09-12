from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .models import DoctorSchedule, Booking
from .serializers import DoctorScheduleSerializer, BookingSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from django.db.models import Case, When
from datetime import datetime, time, timedelta

class DoctorScheduleViewSet(viewsets.ModelViewSet):
    queryset = DoctorSchedule.objects.all()
    serializer_class = DoctorScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        day_order = {
            'Monday': 1,
            'Tuesday': 2,
            'Wednesday': 3,
            'Thursday': 4,
            'Friday': 5,
            'Saturday': 6,
            'Sunday': 7,
        }

        # Annotate each object with its custom order and sort by that annotation
        return DoctorSchedule.objects.filter(doctor=user).annotate(
            day_order=Case(
                *[When(day=day, then=order) for day, order in day_order.items()],
            )
        ).order_by('day_order')

    def create(self, request, *args, **kwargs):
        doc = request.user
        day = request.data.get('day')
        if DoctorSchedule.objects.filter(doctor=doc, day=day).exists():
            return Response(
                {"detail": f"A schedule for {day} already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def available_slots(self, request, pk=None):
        doctor_id = pk
        day = request.query_params.get('day')
        if not day:
            return Response({"detail": "Day is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        schedule = DoctorSchedule.objects.filter(doctor_id=doctor_id, day=day)
        if not schedule.exists():
            return Response({"detail": "No schedule found for this day."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(schedule, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        if not request.data.get('paid', False):
            return Response({'detail': 'Booking cannot be created unless it is paid.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def by_doctor(self, request):
        doctor_id = request.query_params.get('doctor')
        if not doctor_id:
            return Response({'detail': 'Doctor ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        bookings = Booking.objects.filter(doctor_id=doctor_id)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        if not booking.paid:
            return Response({'detail': 'Booking cannot be confirmed until it is paid.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(status='confirmed')  # Update the status or any other field
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        booking = self.get_object()
        new_status = request.data.get('status')
        
        # Check if the status is 'canceled' and if the booking can be canceled
        if new_status == 'canceled' and not booking.can_cancel(request.user):
            return Response({'detail': 'You cannot cancel this booking.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_status not in dict(Booking.STATUS_CHOICES).keys():
            return Response({'detail': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(booking, data={'status': new_status}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def unavailable_slots(self, request):
        doctor_id = request.query_params.get('doctor')
        day = request.query_params.get('day')
        
        if not doctor_id or not day:
            return Response({'detail': 'Doctor ID and day are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        doctor_schedules = DoctorSchedule.objects.filter(doctor_id=doctor_id)
        available_days = doctor_schedules.values_list('day', flat=True)
        unavailable_days = set(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']) - set(available_days)
        
        unavailable_slots = DoctorSchedule.objects.filter(doctor_id=doctor_id, day__in=unavailable_days)
        serializer = DoctorScheduleSerializer(unavailable_slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def user_booked_slots(self, request):
        patient_id = request.user.id
        user_booked_slots = Booking.objects.filter(patient_id=patient_id).values_list('schedule_id', flat=True)
        return Response(list(user_booked_slots), status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def expected_consulting_time(self, request):
        doctor_id = request.query_params.get('doctor')
        date_str = request.query_params.get('date')
        
        if not doctor_id or not date_str:
            return Response({'detail': 'Doctor ID and date are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            day_of_week = date.strftime("%A")

            slot = DoctorSchedule.objects.get(doctor_id=doctor_id, day=day_of_week)
            bookings = Booking.objects.filter(doctor_id=doctor_id, schedule_date=date_str)
            
            # start_time = datetime.strptime(slot.start_time, "%H:%M:%S")
            # end_time = datetime.strptime(slot.end_time, "%H:%M:%S")
            start_time = slot.start_time
            end_time = slot.end_time
                    
            today = datetime.today()
            start_of_day = datetime.combine(today, time(0, 0))
            time_of_start = datetime.combine(today, start_time)
            time_of_end = datetime.combine(today,       end_time)
            new_start_time = time_of_start - start_of_day
            new_end_time = time_of_end - start_of_day
            
                    
            num_bookings = bookings.count()
            if num_bookings == 0:
                expected_time = new_start_time
            else:
                new_time = 5 * num_bookings
                new_time = timedelta(minutes=new_time)
                expected_time = new_start_time + new_time
            
            if expected_time > new_end_time:
                return Response({'error': 'No available slots for the selected date'}, status=status.HTTP_400_BAD_REQUEST)
            
            total_seconds = int(expected_time.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            expected_time = time(hours, minutes, seconds)
            
            formatted_expected_time = expected_time.strftime("%H:%M")
            return Response({'expected_time': formatted_expected_time})
        except DoctorSchedule.DoesNotExist:
            return Response({'error': 'Doctor schedule not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
        