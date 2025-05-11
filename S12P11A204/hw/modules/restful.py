import threading
import asyncio
import aiohttp
import cv2
import numpy as np
from queue import Queue
from datetime import datetime
import base64
from .logger import  app_logger

class RestClientThread(threading.Thread):
    def __init__(self, api_url: str, frame_queue: Queue,robot_id=2,district_id=1,block_id=2):
        """
        Restful로 이미지를 전송할 Thread 
        :param api_url: restful로 전송할 url
        :param frame_queue: 이미지를 저장할 전역 queue
        :param robot_id: 로봇의 id(기본값 : 2)
        :param district_id: 구역의 id(기본값 : 1)
        :param block_id: block의 id(기본값 : 2)
        """
        super().__init__()
        self.api_url = api_url
        self.frame_queue = frame_queue
        self.running = True
        self.robot_id = robot_id
        self.district_id=district_id
        self.block_id = block_id
        
        # asyncio 이벤트 루프
        self.loop = None
        
    async def send_frame(self):
        async with aiohttp.ClientSession() as session:
            while self.running:
                try:
                    # 프레임 가져오기
                    if self.frame_queue.empty():
                        await asyncio.sleep(0.01)
                        continue
                    frame,drain_condition,node = self.frame_queue.get()
                    if frame is None:
                        continue

                    # 프레임을 JPEG로 인코딩 후 base64로 변환
                    _, img_encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                    base64_img = base64.b64encode(img_encoded.tobytes()).decode('utf-8')

                    # JSON 데이터 준비
                    data = {
                        'image': base64_img,
                        'condition': drain_condition,
                        'district_id': self.district_id,
                        'robot_id': self.robot_id
                    }
                    app_logger.info(self.api_url+f"{self.block_id}/receive-img/{node}/"+"   "+f"condition: {data['condition']}, district_id : {data['district_id']}, robot_id:{data['robot_id']}")
                    headers = {'Content-Type': 'application/json'}
                    async with session.post(self.api_url+f"{self.block_id}/receive-img/{node}/", json=data, headers=headers) as response:
                        if response.status == 200:
                            response_data = await response.json()
                            app_logger.debug(f"Server response: {response_data}")
                        else:
                            app_logger.warning(f"Server returned status code: {response.status}")
                            

                
                except Exception as e:
                    app_logger.error(f"Error sending frame: {str(e)}")
                    await asyncio.sleep(1)  # 에러 발생 시 잠시 대기

    def run(self):
        """스레드의 메인 실행 메서드"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self.send_frame())
        except Exception as e:
            app_logger.error(f"Error in REST client thread: {str(e)}")
        finally:
            self.loop.close()
    
    def stop(self):
        """스레드 정지"""
        self.running = False
        app_logger.info("REST client thread stopping...")
        if self.loop is not None:
            asyncio.run_coroutine_threadsafe(
                self.cleanup(), self.loop
            )
    
    async def cleanup(self):
        """정리 작업"""
        pass

"""
# 사용 예시
if __name__ == "__main__":
    # REST API 엔드포인트 URL
    API_URL = "http://70.12.246.107:8000/video/upload/"
    
    # 프레임 큐 생성
    frame_queue = Queue(maxsize=30)
    
    # REST 클라이언트 스레드 생성 및 시작
    rest_client = RestClientThread(API_URL, frame_queue)
    
    try:
        rest_client.start()
        
        # 테스트를 위한 더미 데이터 전송
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if ret:
                try:
                    frame_queue.put_nowait(frame)
                except Queue.Full:
                    try:
                        frame_queue.get_nowait()
                        frame_queue.put_nowait(frame)
                    except Queue.Empty:
                        pass
            
    except KeyboardInterrupt:
        rest_client.stop()
        rest_client.join()
        cap.release()
"""

class RestLogThread(threading.Thread):
    def __init__(self, api_url: str, log_queue: Queue, robot_id):
        """
        Restful로 로그를 전송할 Thread

        :param api_url: 로그를 전송할 RESTful API의 URL
        :param log_queue: 로그 메시지를 저장할 전역 Queue(main에서 선언하는 전역 queue)
        """
        super().__init__()
        self.api_url = api_url
        self.log_queue = log_queue
        self.running = True
        self.robot_id = robot_id
#        self.district_id = district_id
#        self.block_id = block_id
#        self.node_id = node_id

        # asyncio 이벤트 루프 (스레드 내에서 별도로 생성)
        self.loop = None

    async def send_logs(self):
        async with aiohttp.ClientSession() as session:
            while self.running:
                try:
                    # 로그 메시지를 큐에서 가져옵니다.
                    
                    if self.log_queue.empty():
                        await asyncio.sleep(0.01)
                        continue
                    app_logger.debug("tyring to get log_queue")
                    log_message = self.log_queue.get()

                    # API URL 예시 (필요에 따라 block_id 등을 경로에 포함)
                    url = self.api_url + f"{self.robot_id}/receive_log/"
                    app_logger.info(f"Sending log to {url} with data: {log_message}")

                    headers = {'Content-Type': 'application/json'}
                    # post method
                    async with session.post(url, json=log_message, headers=headers) as response:
                        if response.status == 200 or response.status == 201:
                            response_data = await response.json()
                            app_logger.debug(f"Server response: {response_data}")
                        else:
                            app_logger.warning(f"Server returned status code: {response.status}")

                except Exception as e:
                    app_logger.error(f"Error sending log: {str(e)}")
                    await asyncio.sleep(1)  # 예외 발생 시 잠시 대기

    def run(self):
        """스레드의 메인 실행 메서드: asyncio 이벤트 루프를 생성하고, send_logs() 코루틴을 실행합니다."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.send_logs())
        except Exception as e:
            app_logger.error(f"Error in REST client thread: {str(e)}")
        finally:
            self.loop.close()

    def stop(self):
        """스레드 정지 요청"""
        self.running = False
        app_logger.info("REST client thread stopping...")
        if self.loop is not None:
            asyncio.run_coroutine_threadsafe(self.cleanup(), self.loop)

    async def cleanup(self):
        """필요한 정리 작업 수행 (현재는 pass로 처리)"""
        pass

# 사용 예시
if __name__ == "__main__":
    # 실제 로그 전송용 API 엔드포인트 URL로 변경하세요.
    API_URL = "http://70.12.246.107:8000/log/upload/"

    # 로그 메시지를 저장할 큐 생성 (최대 30개)
    log_queue = Queue(maxsize=30)

    # REST 클라이언트 스레드 생성 및 시작
    rest_client = RestClientThread(API_URL, log_queue)
    rest_client.start()

    import time
    try:
        while True:
            # 테스트를 위한 로그 메시지 전송: 1초마다 로그 메시지를 큐에 넣습니다.
            log_message = f"Test log message at {datetime.now().isoformat()}"
            log_queue.put(log_message)
            time.sleep(1)
    except KeyboardInterrupt:
        rest_client.stop()
        rest_client.join()

