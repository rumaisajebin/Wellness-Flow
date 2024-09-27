# from rest_framework.response import Response  
# from rest_framework import viewsets
# from .models import Message, Room
# from .serializer import ChatMessageSerializer
# from rest_framework import status

# class ChatMessageViewSet(viewsets.ModelViewSet):
#     queryset = Message.objects.all()
#     serializer_class = ChatMessageSerializer

#     def get_queryset(self):
#         room_name = self.kwargs['room_name']
#         print(f"Fetching messages for room: {room_name}")
        
#         # Check if the room exists, if not, create it
#         room, created = Room.objects.get_or_create(room_name=room_name)
#         if created:
#             print(f"New room created from view.py: {room_name}")
        
#         # Return messages filtered by the existing or newly created room
#         return self.queryset.filter(room=room)
    
#     def create(self, request, *args, **kwargs):
#         room_name = self.kwargs['room_name']
#         room, created = Room.objects.get_or_create(room_name=room_name)
        
#         if created:
#             print(f"New room created from view.py (create): {room_name}")
            
#         data = request.data.copy()
#         data['room'] = room.id  # Attach the room to the message
#         # data['sender'] = request.data.get('sender')  # Ensure sender ID is included

#         print("Received Data======/n========/n========:", data)  # Debug incoming data

#         serializer = self.get_serializer(data=data)
#         if serializer.is_valid():
#             try:
#                 print("serializer check")
#                 self.perform_create(serializer)
#                 print("Message Created:", serializer.data)  # Debug successful message creation
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             except Exception as e:
#                 print(f"Error saving message: {e}")  # Catch and log any exceptions
#                 return Response({"error": "Could not save message"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         else:
#             print("Validation Errors:", serializer.errors)  # Debug validation errors
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Message
from .serializer import ChatSerializer
from django.db.models import Q
from account.models import CustomUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from rest_framework.views import APIView


class MessageViewSet(viewsets.ViewSet):
    
    def list(self, request, room_name):
        # Split room_name to get sender and receiver IDs
        try:
            sender_id, receiver_id = room_name.split('_')
        except ValueError:
            return Response({'error': 'Invalid room name format'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch messages for the specific room
        messages = Message.objects.filter(
            Q(sender_id=sender_id, receiver_id=receiver_id) | 
            Q(sender_id=receiver_id, receiver_id=sender_id)
        ).order_by('timestamp')

        serializer = ChatSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SendMessage(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser, MultiPartParser, FormParser)  # Added JSONParser

    def post(self, request, *args, **kwargs):
        message = request.data.get('message')
        sender_id = request.data.get('sender')
        receiver_id = request.data.get('receiver')

        if not sender_id or not receiver_id:
            return Response({"error": "Sender and receiver are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sender = CustomUser.objects.get(id=sender_id)
            receiver = CustomUser.objects.get(id=receiver_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid sender or receiver"}, status=status.HTTP_400_BAD_REQUEST)

        chat = Message(sender=sender, receiver=receiver, message=message)

        serializer = ChatSerializer(chat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)