from rest_framework import serializers
from .models import Slot, Booking, TimeSlot

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = '__all__'
    
class SlotSerializer(serializers.ModelSerializer):
    time_slot = TimeSlotSerializer(read_only=True, source='time')
    
    class Meta:
        model = Slot
        fields = ['id', 'start_date', 'end_date', 'time', 'time_slot', 'is_booked', 'doctor']
        
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        time = data.get('time')
        
        if start_date > end_date:
            raise serializers.ValidationError("End date cannot be earlier than start date.")
        
        if not time:
            raise serializers.ValidationError("A valid time slot must be selected.")
        
        # Optionally, check for overlapping slots
        doctor = data.get('doctor')
        overlapping_slots = Slot.objects.filter(
            doctor=doctor,
            start_date__lte=end_date,
            end_date__gte=start_date,
            time=time
        ).exclude(id=self.instance.id if self.instance else None)
        
        if overlapping_slots.exists():
            raise serializers.ValidationError("This time slot overlaps with an existing slot.")
        
        return data
        
class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
