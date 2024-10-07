from rest_framework import serializers
from .models import VideoCallSession

class VideoCallSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoCallSession
        fields = ['appointment', 'video_start_time', 'video_end_time']

    def validate(self, data):
        """
        Custom validation to ensure that video_start_time is before video_end_time.
        """
        if data['video_start_time'] >= data['video_end_time']:
            raise serializers.ValidationError("Video start time must be before the end time.")
        return data
 