from channels.generic.websocket import AsyncJsonWebsocketConsumer

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_group_name = None  # ✅ MUHIM

        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return

        try:
            other_user_id = int(
                self.scope["url_route"]["kwargs"]["user_id"]
            )
        except (KeyError, ValueError):
            await self.close()
            return

        ids = sorted([self.user.id, other_user_id])
        self.room_group_name = f"chat_{ids[0]}_{ids[1]}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if self.room_group_name:  # ✅ MUHIM
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def chat_message(self, event):
        await self.send_json(event["message"])

        
class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        self.group_name = f"notify_{self.user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        print("🔔 NOTIFY CONNECT:", self.user.id)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def notify(self, event):
        await self.send_json(event["data"])
