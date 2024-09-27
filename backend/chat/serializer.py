from rest_framework import serializers
from .models import Message, Room
from account.models import CustomUser

class ChatMessageSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room.room_name', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'room', 'room_name', 'sender', 'receiver', 'message', 'timestamp']

    def validate(self, data):
        """
        Validate that sender, receiver, message, and room are provided.
        """
        # Validate sender
        if 'sender' not in data or not data['sender']:
            raise serializers.ValidationError("Sender is required.")
        
        # Validate receiver
        if 'receiver' not in data or not data['receiver']:
            raise serializers.ValidationError("Receiver is required.")
        
        # Validate message content
        if 'message' not in data or not data['message']:
            raise serializers.ValidationError("Message content is required.")
        
        # Validate room existence based on room_id
        # room_id = data.get('room')
        # if room_id:
        #     try:
        #         room = Room.objects.get(id=room_id)
        #         data['room'] = room  # Optionally assign the room object to data
        #     except Room.DoesNotExist:
        #         raise serializers.ValidationError("Room with the specified ID does not exist.")
        # else:
        #     raise serializers.ValidationError("Room ID is required.")

        return data

    def create(self, validated_data):
        # Use the validated data to create a new Message instance
        message = Message.objects.create(
            room=validated_data['room'],
            sender=validated_data['sender'],
            receiver=validated_data['receiver'],
            message=validated_data['message']
        )
        return message
    
from rest_framework import serializers
from .models import CustomUser, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'password', 'is_active', 'is_verify']
        extra_kwargs = {'password': {'write_only': True}}

class ChatSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    
    
    room_name = serializers.CharField(source='room.room_name', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'room', 'room_name', 'sender', 'receiver', 'message', 'timestamp']
