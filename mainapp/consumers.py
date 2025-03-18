import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from .models import Chat, ChatRoom

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Get or create the chat room
        self.chatroom = await self.get_chatroom(self.room_name)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        sender_username = data["username"]

        # Save message to database
        sender = await self.get_user(sender_username)
        chat = await self.save_message(self.chatroom, sender, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": sender.username,
                "timestamp": chat.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def get_chatroom(self, room_name):
        user1, user2 = room_name.split("_")
        user1_obj = User.objects.get(username=user1)
        user2_obj = User.objects.get(username=user2)
        return ChatRoom.objects.get_or_create(user1=user1_obj, user2=user2_obj)[0]

    @sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @sync_to_async
    def save_message(self, chatroom, sender, message):
        return Chat.objects.create(chatroom=chatroom, sender=sender, message=message)