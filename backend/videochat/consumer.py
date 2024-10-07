import json
from channels.generic.websocket import AsyncWebsocketConsumer

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        
        try:
            # Extract sender and receiver IDs from room name
            sender_id, receiver_id = self.room_name.split('_')
            print(f"VideoSender ID: {sender_id}, VideoReceiver ID: {receiver_id}")
        except ValueError as e:
            print(f"Error splitting room_name: {e}")
            await self.close()
            return
            
        self.room_group_name = f'video_call_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        print(f"User joined room: {self.room_name}")

        # Notify other users in the group that a new user has joined
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'user_joined',
            'message': {'user': self.channel_name, 'action': 'joined'}
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        print(f"User left room: {self.room_name}")

        # Notify others in the group that a user has left
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'user_left',
            'message': {'user': self.channel_name, 'action': 'left'}
        })

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        peer_id = text_data_json.get('peer_id')

        print(f"Received action: {action}, from room: {self.room_name}, peer ID: {peer_id}")

        sender_id, receiver_id = self.room_name.split('_')

        # Handle call action
        if action == "call":
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'video_call_message',
                'action': 'call',
                'peer_id': peer_id,
                'receiver_id': receiver_id,
            })
            print(f"Sent call notification for room: {self.room_name}, peer ID: {peer_id} to receiver ID: {receiver_id}")

        # Handle answered or rejected action
        elif action in ["answered", "rejected"]:
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'video_call_message',
                'action': action,
                'peer_id': peer_id,
                'receiver_id': receiver_id,
            })
            print(f"Sent {action} notification for room: {self.room_name}, peer ID: {peer_id} to receiver ID: {receiver_id}")

        else:
            print(f"Unknown action received: {action}")

    async def video_call_message(self, event):
        await self.send(text_data=json.dumps({
            'action': event['action'],
            'peer_id': event['peer_id'],
            'receiver_id': event['receiver_id'],
        }))

    async def user_joined(self, event):
        await self.send(text_data=json.dumps(event['message']))

    async def user_left(self, event):
        await self.send(text_data=json.dumps(event['message']))
