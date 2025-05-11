import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from channels.exceptions import ChannelFull
import cv2
import numpy as np
import logging
import asyncio
import time

logger = logging.getLogger(__name__)


# 비디오 스트리밍을 프론트에 전송하는 함수
class VideoStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("video_stream", self.channel_name)
        logger.info(f"WebSocket connection established: {self.channel_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("video_stream", self.channel_name)
        logger.info(f"WebSocket connection closed: {self.channel_name}, code: {close_code}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            frame = data.get('frame')
            timestamp = data.get('timestamp')

            if not frame or not timestamp:
                raise ValueError("Missing 'frame' or 'timestamp' in received data")

            logger.debug(f"Received frame data at {timestamp}")
            # print(f"프레임 수신: timestamp {timestamp}")

            img_data = base64.b64decode(frame)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None or img.size == 0:
                raise ValueError("Received image is empty or None")

            processed_img = img
            
            _, buffer = cv2.imencode('.jpg', processed_img)
            processed_frame = base64.b64encode(buffer).decode('utf-8')

            await self.channel_layer.group_send(
                "video_stream",
                {
                    "type": "send_frame_to_frontend",
                    "frame": processed_frame,
                    "timestamp": timestamp
                }
            )

        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            await self.channel_layer.group_send(
                "video_stream",
                {
                    "type": "send_frame_to_frontend",
                    "error": str(e),
                    "timestamp": time.time()
                }
            )

    async def send_frame_to_frontend(self, event):
        if 'error' in event:
            await self.send(text_data=json.dumps({
                'error': event['error'],
                'status': 'error',
                'timestamp': event['timestamp']
            }))
        else:
            await self.send(text_data=json.dumps({
                'frame': event['frame'],
                'timestamp': event['timestamp'],
                'status': 'success'
            }))


class JSONReceiveConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        logger.info("WebSocket connection established")

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected with code: {close_code}")

    async def receive(self, text_data):
        try:
            # JSON 데이터 파싱
            data = json.loads(text_data)
            
            # 데이터 검증
            if not isinstance(data, dict):
                await self.send(text_data=json.dumps({
                    'status': 'error',
                    'message': 'Invalid JSON format'
                }))
                return

            # 로깅
            logger.info(f"Received JSON data: {data}")

            # 데이터 처리 성공 응답
            await self.send(text_data=json.dumps({
                'status': 'success',
                'message': 'JSON data received successfully',
                'received_data': {
                    'keys': list(data.keys()),
                    'total_keys': len(data)
                }
            }))

        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
            await self.send(text_data=json.dumps({
                'status': 'error',
                'message': 'Invalid JSON format'
            }))

        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            await self.send(text_data=json.dumps({
                'status': 'error',
                'message': str(e)
            }))

# 로봇 활성화를 명령하는 함수
class RobotConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("robot", self.channel_name)
        logger.info(f"WebSocket connection established: {self.channel_name}")


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("video_stream", self.channel_name)
        logger.info(f"WebSocket connection closed: {self.channel_name}, code: {close_code}")

    async def robot_assignment(self, event):
        message = event['message']
        logger.info(f"Received robot_assignment message: {message}")
        await self.send(text_data=json.dumps({
            'command': 'activate',
            'type': 'robot_assignment',
            'robot_id': message['robot_id'],
            'assigned_drains': message['assigned_drains'],
            # 'route': message['route']
        }))

    async def robot_deactivate(self, event):
        message = event['message']
        logger.info(f"Received robot_status message: {message}")
        await self.send(text_data=json.dumps({
            'command': message['command'],
            'type': 'robot_deactivate',
            'robot_id': message['robot_id']
        }))
    # async def robot_deactivate(self, event):
    #     message = event['message']
    #     logger.info(f"Received robot_status message: {message}")
    #     await self.send(text_data=json.dumps({
    #         'command': 'deactivate',
    #         'type': 'robot_deactivate',
    #         'robot_id': message['robot_id']
    #     }))    

class DrainUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "drain_updates",
            self.channel_name
        )
        await self.accept()
        logger.info(f"WebSocket connection established: {self.channel_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "drain_updates",
            self.channel_name
        )
        logger.info(f"WebSocket connection closed: {self.channel_name}, code: {close_code}")

    async def receive(self, text_data):
        logger.info(f"Received message from client: {text_data}")

    async def drain_update(self, event):
        try:
            logger.info(f"Drain update event received: {event}")
            message = event['message']
            text_data = json.dumps(message)
            
            logger.info(f"Sending data to frontend: {text_data}")
            
            await self.send(text_data=text_data)
            logger.info(f"Data sent to frontend: {self.channel_name}")
        except Exception as e:
            logger.error(f"Error in drain_update: {e}", exc_info=True)