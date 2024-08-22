from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .models import DoctorSchedule, Booking
from .serializers import DoctorScheduleSerializer, BookingSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError

class DoctorScheduleViewSet(viewsets.ModelViewSet):  # Renamed to avoid conflict
    queryset = DoctorSchedule.objects.all()
    serializer_class = DoctorScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return  DoctorSchedule.objects.filter(doctor=user)
    
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
        try:
            schedule = DoctorSchedule.objects.filter(doctor=pk).values('id', 'day', 'start_time', 'end_time')
            return Response(schedule, status=status.HTTP_200_OK)
        except DoctorSchedule.DoesNotExist:
            return Response({'detail': 'No schedule found.'}, status=status.HTTP_404_NOT_FOUND)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        print(self.request.data)
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
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
        
        try:
            bookings = Booking.objects.filter(doctor_id=doctor_id)
            serializer = self.get_serializer(bookings, many=True)
            return Response(serializer.data)
        except Booking.DoesNotExist:
            return Response({'detail': 'No bookings found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        serializer = self.get_serializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(status='confirmed')  # Update the status or any other field
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        booking = self.get_object()
        new_status = request.data.get('status')
        
        # Validate new status
        if new_status not in dict(Booking.STATUS_CHOICES).keys():
            return Response({'detail': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(booking, data={'status': new_status}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)