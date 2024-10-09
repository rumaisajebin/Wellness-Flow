import json
from channels.generic.websocket import AsyncWebsocketConsumer

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']

        try:
            current_user_id = self.scope['url_route']['kwargs'].get('current_user_id')
            self.sender_id, self.receiver_id = self.room_name.split('_')
            if self.sender_id == current_user_id:
                pass  
            else:
                self.sender_id, self.receiver_id = current_user_id, self.sender_id
            print(f"Video Sender ID: {self.sender_id}, Video Receiver ID: {self.receiver_id}")

        except ValueError:
            print("Error: Room name format is invalid. It should be 'senderId_receiverId'.")
            await self.close()
            return
        except Exception as e:
            print(f"Error in connect method: {e}")
            await self.close()
            return

        # Define the room group name for the WebSocket connection
        self.room_group_name = f'video_call_{self.room_name}'

        # Add the channel to the room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Accept the WebSocket connection
        await self.accept()

        # Notify the group that a user has joined
        message = {
            'user': {'id': self.sender_id, 'username': f"User {self.sender_id}"},
            'action': 'joined',
            'remotePeerId': self.receiver_id,
        }

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'user_joined',
            'message': message
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"User left room: {self.room_name}")

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'user_left',
            'message': {'user': {'id': self.sender_id}, 'action': 'left'}
        })

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        peer_id = data.get('peer_id')

        print(f"Received action: {action}, from room: {self.room_name}, peer ID: {peer_id}")

        try:
            current_user_id = self.scope['url_route']['kwargs'].get('current_user_id')
            self.sender_id, self.receiver_id = self.room_name.split('_')
            if self.sender_id == current_user_id:
                pass  
            else:
                self.sender_id, self.receiver_id = current_user_id, self.sender_id
        except ValueError as e:
            print(f"Error splitting room_name: {e}")
            await self.close()
            return
        
        if action == "join":
            message = {
                'user': {'id': self.sender_id, 'username': f"User {self.sender_id}"},
                'action': 'joined',
                'remotePeerId': self.receiver_id,
                'peer_id': peer_id
            }

            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'user_joined',
                'message': message
            })
            
        if action == "call":
            print("Call action received")
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'video_call_message',
                'action': 'call',
                'peer_id': peer_id,
                'receiver_id': self.receiver_id,
                'remotePeerId': self.receiver_id,
                'user': {'id': self.sender_id}
            })
            print(f"Sent call notification for room: {self.room_name}, peer ID: {peer_id} to receiver ID: {self.receiver_id}")
        
        if action == 'decline':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'video_call_message',
                    'action': 'decline',
                    'user': {'id': data['user_id']},
                    'peer_id': data['peer_id']
                }
            )

        if action == 'end_call':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'video_call_message',
                    'action': 'end_call',
                    'user': {'id': data['user_id']},
                    'peer_id': data['peer_id']
                }
            )

        if action == 'mute':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'video_call_message',
                    'action': 'mute',
                    'user': {'id': data['user_id']},
                    'peer_id': data['peer_id']
                }
            )

        if action == 'unmute':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'video_call_message',
                    'action': 'unmute',
                    'user': {'id': data['user_id']},
                    'peer_id': data['peer_id']
                }
            )

        if action == 'camera_on':
            print('camera_on')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'video_call_message',
                    'action': 'camera_on',
                    'user': {'id': data['user_id']},
                    'peer_id': data['peer_id']
                }
            )

        if action == 'camera_off':
            print('camera_off')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'video_call_message',
                    'action': 'camera_off',
                    'user': {'id': data['user_id']},
                    'peer_id': data['peer_id']
                }
            )
    
    async def video_call_message(self, event):
        await self.send(text_data=json.dumps({
            'action': event['action'],
            'peer_id': event['peer_id'],
            'receiver_id': event['receiver_id'],
            'remotePeerId': event['remotePeerId'],
            'user': event.get('user', {})
        }))

    async def user_joined(self, event):
        user = event['message']['user']
        action = event['message']['action']
        remote_peer_id = event['message'].get('remotePeerId')
        peer_id = event['message'].get('peer_id')

        message = {
            'user': user,
            'action': action,
            'remotePeerId': remote_peer_id,
            'peer_id': peer_id  
        }

        await self.send(text_data=json.dumps(message))

    async def user_left(self, event):
        await self.send(text_data=json.dumps(event['message']))
