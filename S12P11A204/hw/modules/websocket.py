import websockets
import asyncio
import json
from .logger import app_logger
from datetime import datetime
from queue import Queue
import threading
import base64
import cv2
class WebSocketThread(threading.Thread):
    def __init__(self, websocket_url: str, frame_queue: Queue):
        """
        websocket 통신을 담당할 thread class
        :param websocker_url: websocket 통신으로 동영상을 전달할 url
        :param frame_queue: 동영상 저장용으로 사용할 queue
        """
        super().__init__()
        self.websocket_url = websocket_url
        self.frame_queue = frame_queue
        self.running = True 
        
        # asyncio 이벤트 루프
        self.loop = None
    
    async def stream_video(self):
        websocket_options = {
            'ping_interval': 300,  # 300초마다 핑 전송
            'ping_timeout': 1,    # 5초 동안 응답 없으면 연결 종료
        }

        
        while self.running:
            try:
                async with websockets.connect(self.websocket_url, **websocket_options) as websocket:
                    app_logger.info("WebSocket connection established")
                    
                    while self.running:
                        try:
                            if self.frame_queue.empty():
                                await asyncio.sleep(0.01)
                                continue
                            frame_data = self.frame_queue.get()
                            if frame_data is None:
                                await asyncio.sleep(0.01)
                                continue
                            pre_text=""
                            # 프레임 인코딩 전후 데이터 확인
                            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
                            _, buffer = cv2.imencode('.jpg', frame_data, encode_param)
                            #app_logger.debug(f"Encoded buffer size: {len(buffer)}")
                            jpg_as_text = base64.b64encode(buffer).decode()
                            if(pre_text==jpg_as_text):
                                print("오류")
                            pre_text=jpg_as_text
                            # Send frame via WebSocket            
                            await websocket.send(json.dumps({
                                "frame": jpg_as_text,
                                "timestamp": datetime.now().isoformat()
                            }))
                        except Exception as e:
                            app_logger.error(f"Error processing frame: {str(e)}")
                            break                
            except websockets.exceptions.ConnectionClosed:
                app_logger.warning("WebSocket connection closed, attempting to reconnect...")
                await asyncio.sleep(0.1)
            except Exception as e:
                app_logger.error(f"WebSocket error: {str(e)}")
                await asyncio.sleep(0.3)
    
    def run(self):
        """스레드의 메인 실행 메서드"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self.stream_video())
        except Exception as e:
            app_logger.error(f"Error in WebSocket thread: {str(e)}")
        finally:
            self.loop.close()
    
    def stop(self):
        """스레드 정지"""
        self.running = False
        app_logger.info("WebSocket thread stopping...")
        if self.loop is not None:
            # 이벤트 루프가 실행 중이면 안전하게 종료
            asyncio.run_coroutine_threadsafe(
                self.cleanup(), self.loop
            )
    
    async def cleanup(self):
        """정리 작업"""
        try:
            # 큐 비우기
            while not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except:
                    break
            
            # 잠시 대기하여 진행 중인 작업이 완료될 수 있도록 함
            await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass  # 작업이 취소되어도 무시
        

# 사용 예시
if __name__ == "__main__":
    # WebSocket 서버 URL
    WEBSOCKET_URL = "ws://70.12.246.107:8000/ws/video_stream/"
    
    # 프레임 큐 생성
    frame_queue = Queue(maxsize=30)
    
    # WebSocket 스레드 생성 및 시작
    ws_thread = WebSocketThread(WEBSOCKET_URL, frame_queue)
    
    try:
        ws_thread.start()
        
        # 테스트를 위한 더미 데이터 전송
        while True:
            # 실제로는 여기서 카메라 프레임을 전송
            frame_data = {"test": "data"}
            frame_queue.put(frame_data)
            asyncio.sleep(0.03)  # 약 30 FPS
            
    except KeyboardInterrupt:
        ws_thread.stop()
        ws_thread.join()  # 스레드가 완전히 종료될 때까지 대기
