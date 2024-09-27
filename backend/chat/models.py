from django.db import models
from account.models import CustomUser

# Create your models here.

class Room(models.Model):
    room_name = models.CharField(max_length=50,unique=True)
    
    def __str__(self):
        return self.room_name

class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_messages',on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name='receiver_messages',on_delete=models.CASCADE)
    room = models.ForeignKey(Room,on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
         return f"{self.sender.username} to {self.receiver.username}: {self.message[:20]}"