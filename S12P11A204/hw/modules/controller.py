import cv2
import time
import numpy as np
from collections import deque
from queue import Queue
from datetime import datetime

from modules.linetrace import Linetracer
from modules.mobile_net_module import MobileNetClassifier
from modules.yolo_module import YOLODetector
from modules.logger import app_logger
from modules.websocket import WebSocketThread
from modules.restful import RestClientThread, RestLogThread
from modules.pathconvert import findPath
from modules.config import (
    WS_VIDEO_STREAM_URL, REST_DRAIN_URL, REST_ROBOT_INFO_URL,
    ROBOT_CONFIG, CAMERA_CONFIG, QUEUE_CONFIG, LINETRACER_CONFIG,
    GREEN_HSV_RANGE, BIAS_DICT, NODE_MAP, COOLDOWN_TIME, GREEN_RATIO_THRESHOLD
)

class RobotController:
    states = ['off', 'loading', 'idle', 'active']

    def __init__(self):
        # 추후 각 모듈을 load_models에서 초기화하므로 초기값은 None으로 둡니다.
        self.linetracer = None
        self.yolo = None
        self.mobile = None
        self.cap = None

        # 웹소켓/RESTful 관련 큐와 스레드 (load_models에서 초기화)
        # queue
        self.frame_queue = None
        self.image_queue = None
        self.log_queue = None
        # threads 
        self.web_frame = None
        self.restful_frame = None
        self.restful_log = None

        # 외부 명령 전달을 위한 큐 (run_idle 또는 run_active에서 할당)
        self.command_queue = None

        # ACTIVE 상태 관련 변수
        self.q = None
        self.bias_dict = BIAS_DICT
        self.last_yolo_time = 0
        self.cooldown = COOLDOWN_TIME
        self.line_change = True
        self.fps = CAMERA_CONFIG['fps']
        self.frame_interval = 1.0 / self.fps
        self.last_frame_time = time.time()
        self.result = None
        self.Map = NODE_MAP
        self.robot_id = ROBOT_CONFIG['robot_id']
        self.district_id = ROBOT_CONFIG['district_id']
        self.block_id = ROBOT_CONFIG['block_id']
        self.capture_flag = False

        # 초록색 HSV 범위 설정
        self.lower_green = np.array(GREEN_HSV_RANGE['lower'])
        self.upper_green = np.array(GREEN_HSV_RANGE['upper'])

    def load_models(self):
        app_logger.info("모델, 카메라 및 관련 쓰레드 로드 중...")
        # linetracer, YOLO, MobileNet 모델 초기화
        self.linetracer = Linetracer()
        self.yolo = YOLODetector()
        self.mobile = MobileNetClassifier()

        # 카메라 초기화
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_CONFIG['width'])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_CONFIG['height'])
        self.cap.set(cv2.CAP_PROP_FPS, CAMERA_CONFIG['fps'])
        cv2.namedWindow('Original Frame', cv2.WINDOW_NORMAL)

        # 웹소켓 및 RESTful 처리를 위한 큐와 스레드 초기화
        self.frame_queue = Queue(maxsize=QUEUE_CONFIG['frame_queue_size'])
        self.image_queue = Queue(maxsize=QUEUE_CONFIG['image_queue_size'])
        self.log_queue = Queue(maxsize=QUEUE_CONFIG['log_queue_size'])
        
        self.web_frame = WebSocketThread(WS_VIDEO_STREAM_URL, self.frame_queue)
        self.restful_frame = RestClientThread(
            REST_DRAIN_URL, 
            self.image_queue, 
            self.robot_id, 
            self.district_id, 
            self.block_id
        )
        self.restful_log = RestLogThread(
            REST_ROBOT_INFO_URL, 
            self.log_queue, 
            self.robot_id
        )

        app_logger.info("모델, 카메라 및 쓰레드 초기화 완료.")

        if self.web_frame is not None:
            self.web_frame.start()
        if self.restful_frame is not None:
            self.restful_frame.start()
        if self.restful_log is not None:
            self.restful_log.start()

    def stop_threads(self):
        if self.web_frame is not None:
            self.web_frame.stop()
            print("webframe stop")
            self.web_frame.join()
            print("webframe join")
        if self.restful_frame is not None:
            self.restful_frame.stop()
            print("restful_frame.stop")
            self.restful_frame.join()
            print("restful_frame.join")
        if self.restful_log is not None:
            self.restful_log.stop()
            print("restful_log.stop")
            self.restful_log.join()
            print("restful_log.join")

    def run_idle(self, cmd_queue):
        """
        idle 상태에서는 카메라 프레임에 "IDLE" 텍스트를 표시하며
        외부 명령(cmd_queue)을 대기하다가 "activate" 명령 수신 시 active 상태로 전이합니다.
        """
        app_logger.info("현재 idle 상태입니다. 외부 명령 대기 중...")
        self.command_queue = cmd_queue
        while True:
            try:
                cmd = self.command_queue.get_nowait()
            except:
                cmd = None

            if cmd is not None:
                app_logger.info(f"idle 상태에서 명령 수신: {cmd}")
                # 명령이 dict 형태이면 "command" 키 확인
                if isinstance(cmd, dict) and "command" in cmd:
                    command_str = cmd["command"].lower()
                else:
                    command_str = str(cmd).lower()

                if command_str == "activate":
                    self.activate()  # FSM trigger: idle → active
                    self.q = findPath(cmd)
                    print(f"route : {self.q}")
                    break

            # idle 상태에서는 간단히 카메라 프레임을 보여줍니다.
            ret, frame = self.cap.read()
            if ret:
                cv2.putText(frame, "IDLE", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow('Idle Frame', frame)
            if not self.frame_queue.full():
                self.frame_queue.put_nowait(frame)
            cv2.waitKey(1)
            time.sleep(0.1)

    def run_active(self, cmd_queue):
        """
        active 상태에서는 프레임을 처리하며,
        외부 명령(cmd_queue)으로 "deactivate" 명령 수신 시 idle 상태로 전이합니다.
        """
        app_logger.info("active 상태: 프레임 처리를 시작합니다.")
        self.command_queue = cmd_queue
        self.linetracer.edge_value = self.q[0][0]
        self.linetracer.steering_bias = self.bias_dict[self.q[0][0]]
        self.capture_flag = self.q[0][1]
        self.q.popleft()         
        self.linetracer.speed_gain=LINETRACER_CONFIG['speed_gain'],
        self.linetracer.steering_gain=LINETRACER_CONFIG['steering_gain']
        try:
            while True:
                # 외부 명령 확인
                try:
                    cmd = self.command_queue.get_nowait()
                except:
                    cmd = None

                if cmd is not None:
                    app_logger.info(f"active 상태에서 명령 수신: {cmd}")
                    if isinstance(cmd, dict) and "command" in cmd:
                        command_str = cmd["command"].lower()
                    else:
                        command_str = str(cmd).lower()

                    if command_str == "deactivate":
                        self.deactivate()
                        self.linetracer.stop()  # FSM trigger: active → idle
                        break

                ret, frame = self.cap.read()
                if not ret:
                    app_logger.error("카메라 프레임 캡쳐 실패")
                    break
                current_time = time.time()
                cv2.imshow('Original Frame', frame)
                if not self.frame_queue.full():
                    self.frame_queue.put_nowait(frame)

                # 초록색 로그 출력
                if self.linetracer.edge_value==3 and self.checkGreen(frame):
                    if self.capture_flag:
                        log_message = {
                            'timestamp': datetime.now().isoformat(),
                            'district_id': self.district_id,
                            'robot_id': self.robot_id, 
                            'end' : True
                        } 
                        self.log_queue.put_nowait(log_message)
                        self.deactivate()
                        self.linetracer.robot.stop()
                        break
                    elif self.q:
                        self.linetracer.edge_value,self.capture_flag = self.q[0]
                        self.linetracer.steering_bias = self.bias_dict[self.linetracer.edge_value]
                        self.q.popleft()

                
                # 라인트레이서 처리
                self.linetracer.process_frame(frame) 
                #app_logger.debug(f"speed: {self.linetracer.speed_gain}, steering: {self.linetracer.steering_gain} edge: {self.linetracer.edge_value}, bias: {self.linetracer.steering_bias}")
                # YOLO에서 이미지를 검출하는 조건문
                if self.line_change:
                    self.result = self.yolo.process_frame(frame)
                else:
                    self.result = None

                if self.result is not None and self.line_change:
                    # log_message queue에 데이터 전달
                    log_message = {
                        'timestamp': datetime.now().isoformat(),
                        'district_id': self.district_id,
                        'robot_id': self.robot_id, 
                        'node_id' : self.Map[self.linetracer.edge_value]
                    } 
                    print(f"log message : {log_message}")
                    self.log_queue.put_nowait(log_message)
                    app_logger.debug(f"put log to log_queue {log_message}")

                    # 기존 속도/조향 값 저장 후 로봇 정지
                    pre_speed_gain = self.linetracer.speed_gain
                    pre_steering_gain = self.linetracer.steering_gain
                    pre_steering_bias = self.linetracer.steering_bias
                    pre_edge_value = self.linetracer.edge_value

                    self.linetracer.speed_gain = 0.0
                    self.linetracer.steering_gain = 0.0
                    self.linetracer.steering_bias = 0.0
                    self.linetracer.robot.stop()

                    # YOLO가 탐지한 영역 crop 후 MobileNet 예측
                    crop_frame = None
                    if self.capture_flag:
                        crop_frame = self.mobile.crop_image(frame, self.result)
                        predicted_class, confidence = self.mobile.predict(crop_frame)
                        app_logger.debug(f"class: {predicted_class}, confidence: {confidence:.2f}")

                    if self.q:
                        self.linetracer.edge_value,self.capture_flag = self.q[0]
                        self.linetracer.steering_bias = self.bias_dict[self.linetracer.edge_value]
                        self.q.popleft()

                    self.linetracer.steering_gain = pre_steering_gain
                    self.linetracer.speed_gain = pre_speed_gain

                    if crop_frame is not None:
                        cv2.imshow('Cropped Frame', crop_frame)
                        frame_copy = frame.copy()
                        self.mobile.draw_result(frame_copy, self.result, predicted_class, confidence)
                        cv2.imshow('Draw Frame', frame_copy)
                        try:
                            self.image_queue.put_nowait((frame_copy, predicted_class, self.Map.get(pre_edge_value, 0)))
                        except Exception as e:
                            app_logger.error(f"image_queue 에러: {e}")
                            if not self.image_queue.empty():
                                self.image_queue.get_nowait()
                    self.line_change = False
                    self.last_yolo_time = time.time()
                    self.result = None

                # cooldown 이후 다시 line_change 활성화
                if current_time - self.last_yolo_time >= self.cooldown:
                    self.line_change = True

                key = cv2.waitKey(1) & 0xFF
                if key in [ord('q'), 27]:
                    app_logger.info("키 입력에 의해 active 모드 종료")
                    break

        except KeyboardInterrupt:
            app_logger.critical("Ctrl+C 입력으로 active 모드 중단")
            

        finally:
            # log_message queue에 데이터 전달
            pass

    def cleanup(self):
        app_logger.info("자원 정리 중...")
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        if self.linetracer is not None:
            self.linetracer.stop()
        self.stop_threads()
        app_logger.info("정리 완료.")

    def checkGreen(self, frame):
        # 프레임 크기 가져오기
        frame_height, frame_width, _ = frame.shape
        total_pixels = frame_height * frame_width  # 전체 픽셀 수
    
        # BGR을 HSV로 변환
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # 초록색 범위 내에 있는 픽셀을 감지
        mask = cv2.inRange(hsv, self.lower_green, self.upper_green)

        # 초록색 픽셀 개수 계산
        green_pixels = cv2.countNonZero(mask)  # 흰색(255) 픽셀 개수
        green_ratio = (green_pixels / total_pixels) * 100  # 초록색 비율(%)

        # 초록색이 설정된 비율 이상이면 True 반환
        return green_ratio > GREEN_RATIO_THRESHOLD