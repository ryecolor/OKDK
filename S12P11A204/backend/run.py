#1. upload view함수를 실행하는 코드

# import requests

# server_url = 'http://i12a204.p.ssafy.io:8000/video/upload/'
# video_path = 'media/videos/subtask1시연영상.mp4'

# try:
#     with open(video_path, 'rb') as video_file:
#         files = {'video': video_file}
#         response = requests.post(server_url, files=files)
#         response.raise_for_status()
#         print(response.text)
#         try:
#             print(response.json())
#         except requests.exceptions.JSONDecodeError:
#             print("Response content is not valid JSON")
#             print(response.text)
# except Exception as e:
#     print(f"Error: {str(e)}")




#2. 다운로드 view함수를 실행하는 코드드
# import requests

# server_url = 'http://localhost:8000/video/download/'

# try:
#     response = requests.post(server_url)
#     print(response.json())
# except Exception as e:
#     print(f"Error: {str(e)}")




#3. restful api를 이용한 데이터 전송
# import requests
# import json

# url = 'http://localhost:8000/video/logdata/'
# data = {
#     'sensor_id': 'sensor_001',
#     'temperature': 25.5,
#     'humidity': 60.2
# }

# headers = {
#     'Content-Type': 'application/json',
# }

# response = requests.post(url, json=data, headers=headers)


# import asyncio
# import websockets
# import json

# async def send_json_data():
#     # 정확한 WebSocket URL 사용
#     uri = "ws://localhost:8000/ws/json_receive/"
    
#     try:
#         async with websockets.connect(uri) as websocket:
#             # JSON 데이터 생성
#             data = {
#                 'sensor_id': 'sensor_001',
#                 'temperature': 25.5,
#                 'humidity': 60.2
#             }

#             # JSON 데이터 전송
#             await websocket.send(json.dumps(data))

#             # 서버 응답 수신
#             response = await websocket.recv()
#             print(f"Server response: {response}")

#     except Exception as e:
#         print(f"Connection error: {e}")

# asyncio.run(send_json_data())


# 하드웨어에서 더미이미지를 데이터베이스에 저장하는 실행코드
# import requests
# from pathlib import Path
# from PIL import Image
# import io
# import logging
# import json

# # 로깅 설정
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# def create_dummy_image():
#     """더미 이미지 생성"""
#     try:
#         img = Image.new('RGB', (100, 100), color='gray')
#         img_byte_arr = io.BytesIO()
#         img.save(img_byte_arr, format='JPEG')
#         img_byte_arr.seek(0)
#         logger.debug("더미 이미지 생성 성공")
#         return img_byte_arr
#     except Exception as e:
#         logger.error(f"더미 이미지 생성 실패: {str(e)}")
#         raise

# def send_drain_data(drain_condition, block_id, drain_id, base_url="http://i12a204.p.ssafy.io:8000"):
#     """
#     배수구 더미 이미지와 상태 정보를 서버로 전송하는 함수
    
#     Args:
#         drain_condition (str): 배수구 상태 정보
#         block_id (int): 블록 ID
#         drain_id (int): 배수구 ID
#         base_url (str): API 서버 기본 URL
#     """
#     url = f"{base_url}/drain/{block_id}/receive-img/{drain_id}/"
#     logger.info(f"요청 URL: {url}")
#     logger.info(f"배수구 상태: {drain_condition}")
#     logger.info(f"블록 ID: {block_id}")
#     logger.info(f"배수구 ID: {drain_id}")
    
#     try:
#         # 더미 이미지 생성
#         dummy_image = create_dummy_image()
        
#         files = {
#             'image': ('dummy_drain.jpg', dummy_image, 'image/jpeg')
#         }
        
#         data = {
#         'condition': drain_condition 
#         }
        
#         logger.debug("요청 데이터:")
#         logger.debug(f"Files: {files.keys()}")
#         logger.debug(f"Data: {json.dumps(data, ensure_ascii=False)}")
        
#         # PUT 요청으로 변경
#         response = requests.put(
#             url,
#             files=files,
#             data=data
#         )
        
#         # 응답 처리
#         logger.info(f"응답 상태 코드: {response.status_code}")
#         logger.debug(f"응답 헤더: {dict(response.headers)}")
        
#         try:
#             response_data = response.json()
#             logger.debug(f"응답 데이터: {json.dumps(response_data, ensure_ascii=False)}")
#         except json.JSONDecodeError:
#             logger.warning(f"JSON이 아닌 응답: {response.text}")
#             response_data = response.text
        
#         if response.status_code == 200:  # PUT 요청은 200 상태코드 사용
#             logger.info("데이터 전송 성공")
#             return response_data
#         else:
#             logger.error(f"전송 실패: {response.status_code}")
#             return response_data
            
#     except requests.exceptions.RequestException as e:
#         logger.error(f"HTTP 요청 실패: {str(e)}")
#         return None
#     except Exception as e:
#         logger.error(f"예상치 못한 오류 발생: {str(e)}")
#         raise

# if __name__ == "__main__":
#     try:
#         drain_condition = "양호"
#         block_id = 1
#         drain_id = 1
        
#         logger.info("데이터 전송 시작")
#         result = send_drain_data(drain_condition, block_id, drain_id)
#         logger.info("데이터 전송 완료")
#         logger.debug(f"최종 결과: {json.dumps(result, ensure_ascii=False) if result else None}")
        
#     except Exception as e:
#         logger.error(f"메인 실행 중 오류 발생: {str(e)}")

# # 로컬에 저장되어있는 이미지를 데이터베이스로 전송 및 방문한 드레인 큐 수정
# import requests
# from pathlib import Path
# from PIL import Image
# import io
# import logging
# import json
# import os

# # 로깅 설정
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# def get_drain_image(block_id, drain_id):
#     """저장된 배수구 이미지를 읽어오는 함수"""
#     try:
#         # 현재 스크립트의 디렉토리를 기준으로 경로 설정
#         current_dir = Path(__file__).parent
#         image_path = current_dir / 'drain'/ 'images' / f'block_{block_id}' / f'drain_{drain_id}.jpg'
                
#         if not os.path.exists(image_path):
#             logger.error(f"이미지 파일이 존재하지 않습니다: {image_path}")
#             return None
        
#         with open(image_path, 'rb') as img_file:
#             img_data = img_file.read()
        
#         logger.debug(f"배수구 이미지 로드 성공: {image_path}")
#         return io.BytesIO(img_data)
#     except Exception as e:
#         logger.error(f"배수구 이미지 로드 실패: {str(e)}")
#         return None

# def get_robot_queue(robot_id, base_url="http://i12a204.p.ssafy.io:8000"):
#     """로봇의 현재 큐 상태를 가져오는 함수"""
#     try:
#         url = f"{base_url}/robot_info/{robot_id}/get-queue/"
#         response = requests.get(url)
#         response.raise_for_status()  # 오류 발생 시 예외를 발생시킵니다.
#         data = response.json()
#         return data
#     except requests.exceptions.RequestException as e:
#         logger.error(f"로봇 큐 조회 실패: {str(e)}")
#         return None

# def send_drain_data(drain_condition, block_id, drain_id, district_id, robot_id, base_url="http://i12a204.p.ssafy.io:8000"):
#     """배수구 이미지와 상태 정보를 서버로 전송하는 함수"""
#     url = f"{base_url}/drain/{block_id}/receive-img/{drain_id}/"
#     logger.info(f"요청 URL: {url}")
#     logger.info(f"배수구 상태: {drain_condition}")
#     logger.info(f"블록 ID: {block_id}")
#     logger.info(f"배수구 ID: {drain_id}")
    
#     try:
#         drain_image = get_drain_image(block_id, drain_id)
        
#         if drain_image is None:
#             logger.error("배수구 이미지를 로드할 수 없습니다.")
#             return None
        
#         files = {
#             'image': (f'drain_{drain_id}.jpg', drain_image, 'image/jpeg')
#         }
        
#         data = {
#             'condition': drain_condition,
#             'district_id': district_id,
#             'robot_id': robot_id  # 추가된 필드
#         }
        
#         logger.debug("요청 데이터:")
#         logger.debug(f"Files: {files.keys()}")
#         logger.debug(f"Data: {json.dumps(data, ensure_ascii=False)}")
        
#         response = requests.put(
#             url,
#             files=files,
#             data=data
#         )
        
#         logger.info(f"응답 상태 코드: {response.status_code}")
        
#         try:
#             response_data = response.json()
#             logger.debug(f"응답 데이터: {json.dumps(response_data, ensure_ascii=False)}")
#         except json.JSONDecodeError:
#             response_data = response.text
        
#         if response.status_code == 200:
#             logger.info("데이터 전송 성공")
#             return response_data
#         else:
#             logger.error(f"전송 실패: {response.status_code}")
#             return response_data
            
#     except requests.exceptions.RequestException as e:
#         logger.error(f"HTTP 요청 실패: {str(e)}")


# def process_drain_queue(robot_id, base_url="http://i12a204.p.ssafy.io:8000"):  # 집에서 작업 시 localhost로 변경
#     """로봇의 드레인 큐를 처리하는 함수"""
#     try:
#         # 로봇 정보 가져오기
#         robot_url = f"{base_url}/robot_info/{robot_id}/"
#         robot_response = requests.get(robot_url)
#         robot_response.raise_for_status()
#         robot_data = robot_response.json()
#         district_id = robot_data.get('district')  # 로봇의 district_id 가져오기

#         if not district_id:
#             logger.error(f"로봇 {robot_id}에 대한 district 정보가 없습니다.")
#             return

#         # 로봇의 현재 큐 상태 가져오기
#         data = get_robot_queue(robot_id, base_url)
#         if not data:
#             logger.info("처리할 데이터가 없습니다.")
#             return

#         drain_queue = data.get('queue_data', [])
#         if not drain_queue:
#             logger.info("처리할 드레인이 없습니다.")
#             return    
        
#         current_drain_id = drain_queue[0]

#         # ERD에서 drain 테이블의 block_id 외래키 확인
#         drain_details = data.get('drain_details', [])
#         current_drain = next(
#             (drain for drain in drain_details if drain['id'] == current_drain_id),
#             None
#         )

#         if not current_drain:
#             logger.error(f"드레인 {current_drain_id}의 정보를 찾을 수 없습니다.")
#             return
            
#         block_id = current_drain['block']

#         logger.info(f"현재 처리할 드레인: {current_drain_id}")
        
#         # 드레인 데이터 전송 (district_id와 robot_id 추가)
#         result = send_drain_data("위험", block_id, current_drain_id, district_id, robot_id, base_url)

#         if result:
#             logger.info(f"드레인 {current_drain_id} 처리 완료")
        
#     except requests.exceptions.RequestException as e:
#         logger.error(f"HTTP 요청 실패: {str(e)}")
#     except Exception as e:
#         logger.error(f"큐 처리 중 오류 발생: {str(e)}")

# if __name__ == "__main__":
#     try:
#         robot_id = 2  # 처리할 로봇 ID
#         logger.info("로봇 큐 처리 시작")
#         process_drain_queue(robot_id)
#         logger.info("로봇 큐 처리 완료")
        
#     except Exception as e:
#         logger.error(f"메인 실행 중 오류 발생: {str(e)}")


async def send_frame(self):
        async with aiohttp.ClientSession() as session:
            while self.running:
                try:
                    # 프레임 가져오기
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
                    self.logger.info(self.api_url+f"{self.block_id}/receive-img/{node}/"+"   "+f"condition: {data['condition']}, district_id : {data['district_id']}, robot_id:{data['robot_id']}")
                    headers = {'Content-Type': 'application/json'}
                    async with session.post(self.api_url+f"{self.block_id}/receive-img/{node}/", json=data, headers=headers) as response:
                        if response.status == 200:
                            response_data = await response.json()
                            self.logger.debug(f"Server response: {response_data}")
                        else:
                            self.logger.warning(f"Server returned status code: {response.status}")
                            

                
                except Exception as e:
                    self.logger.error(f"Error sending frame: {str(e)}")
                    await asyncio.sleep(1)  # 에러 발생 시 잠시 대기