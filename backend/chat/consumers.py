import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message
from account.models import CustomUser
from .serializer import ChatSerializer
from django.db.models import Q
from datetime import datetime


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        try:
            sender_id, receiver_id = self.room_name.split('_')  # Split room_name into sender and receiver
            print(f"Sender ID: {sender_id}, Receiver ID: {receiver_id}")
        except ValueError as e:
            print(f"Error splitting room_name: {e}")
            
        self.room_group_name = f"{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
        
        # Create or get the room for this conversation
        room, created = await database_sync_to_async(Room.objects.get_or_create)(room_name=self.room_group_name)
        if created:
            print(f"New room created: {self.room_group_name}")
        
        # Join the room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        print("disconnect")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await super().disconnect(code)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        sender_id = text_data_json.get('sender')
        receiver_id = text_data_json.get('receiver')

        if isinstance(sender_id, int):
            sender_id = str(sender_id)
        if isinstance(receiver_id, int):
            receiver_id = str(receiver_id)

        thread_name = f"{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
        chat_message = await self.save_chat_message(message, sender_id, receiver_id, thread_name)

        # Ensure that any datetime object is serialized before sending over WebSocket
        messages = await self.get_messages(sender_id, receiver_id)
        for msg in messages:
            if isinstance(msg.get('timestamp'), datetime):
                msg['timestamp'] = msg['timestamp'].isoformat()  # Convert datetime to ISO 8601 string format

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'messages': messages,
                'sender_id': sender_id,
                'message': message,
            }
        )

    async def chat_message(self, event):
        messages = event.get('messages', [])
        sender_id = event.get('sender_id')
        message = event.get('message')

        await self.send(text_data=json.dumps({
            'messages': messages,
            'sender': {'id': sender_id},
            'message': message
        }))

    @database_sync_to_async
    def save_chat_message(self, message, sender_id, receiver_id, thread_name):
        room, created = Room.objects.get_or_create(room_name=thread_name)
        return Message.objects.create(
            message=message,
            sender_id=sender_id,
            receiver_id=receiver_id,
            room=room  # Save message in the room
        )

    @database_sync_to_async
    def get_messages(self, sender_id, receiver_id):
        thread_name = f"{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
        room = Room.objects.get(room_name=thread_name)
        return list(Message.objects.filter(room=room).order_by('timestamp').values())


    async def mark_message_as_read(self, text_data):
        data = json.loads(text_data)
        message_id = data.get('message_id')
        if message_id:
            await self.mark_as_read(message_id)

    @database_sync_to_async
    def get_user(self, username):
        user = CustomUser.objects.get(username=username)
        print(f"Retrieved user: {user}")  # Debugging statement
        return user
