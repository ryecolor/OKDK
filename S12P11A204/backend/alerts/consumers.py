# alerts/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import json

class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("alerts", self.channel_name)
        await self.accept()
        print("WebSocket 연결 성공")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("alerts", self.channel_name)
        print(f"WebSocket 연결 종료: {close_code}")

    async def send_notification(self, event):
        # 클라이언트로 메시지 전송
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))
        print(f"알림 전송 완료: {event['message']}")

    @classmethod
    async def broadcast_notification(cls, message):
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "alerts",
            {
                "type": "send_notification",
                "message": message
            }
        )