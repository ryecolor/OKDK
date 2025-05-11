import torch
import numpy as np
import PIL.Image
import torchvision.transforms as transforms
from modules.motor import Motor
from modules.resnet_model import ModifiedResNet
from modules.logger import app_logger
from modules.config import LINETRACER_CONFIG

class Linetracer:
    """라인트레이싱을 수행하는 클래스"""
    
    def __init__(self, 
                 speed_gain=LINETRACER_CONFIG['speed_gain'],
                 steering_gain=LINETRACER_CONFIG['steering_gain'],
                 steering_dgain=LINETRACER_CONFIG['steering_dgain'],
                 steering_bias=LINETRACER_CONFIG['steering_bias'],
                 edge_value=LINETRACER_CONFIG['edge_value']): 
        """
        Linetracer 초기화
        
        Args:
            speed_gain (float): 속도 gain 값
            steering_gain (float): steering gain 값
            steering_dgain (float): steering dgain 값
            steering_bias (float): steering bias 값
            edge_value (int): edge value 값
        """
        self.model = self._initialize_model()
        self.speed_gain = speed_gain
        self.steering_gain = steering_gain
        self.steering_dgain = steering_dgain
        self.steering_bias = steering_bias
        self.edge_value = edge_value
        self.robot = Motor()
        self.running = False
        self.angle_last = 0.0
        
        # 전처리를 위한 설정
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.mean = torch.Tensor(LINETRACER_CONFIG['mean']).to(self.device).half()
        self.std = torch.Tensor(LINETRACER_CONFIG['std']).to(self.device).half()

    def _initialize_model(self):
        """
        모델 초기화 및 설정
        
        Returns:
            ModifiedResNet: 준비된 모델
        """
        model = ModifiedResNet()
        return model.load_model().prepare_model()

    def preprocess(self, image, edge_value):
        """
        이미지와 edge value 전처리
        
        Args:
            image: 전처리할 이미지
            edge_value: edge value
            
        Returns:
            tuple: (전처리된 이미지 텐서, edge value 텐서)
        """
        image_tensor = self._preprocess_image(image)
        edge_tensor = self._preprocess_edge_value(edge_value)
        
        return image_tensor.unsqueeze(0), edge_tensor.unsqueeze(0)

    def _preprocess_image(self, image):
        """
        이미지 전처리
        
        Args:
            image: 원본 이미지
            
        Returns:
            torch.Tensor: 전처리된 이미지 텐서
        """
        image_tensor = PIL.Image.fromarray(image)
        image_tensor = transforms.functional.to_tensor(image_tensor).to(self.device).half()
        image_tensor.sub_(self.mean[:, None, None]).div_(self.std[:, None, None])
        
        return image_tensor

    def _preprocess_edge_value(self, edge_value):
        """
        Edge value 전처리
        
        Args:
            edge_value: 원본 edge value
            
        Returns:
            torch.Tensor: 전처리된 edge value 텐서
        """
        return torch.tensor(float(edge_value) / 4.0).to(self.device).half()

    def process_frame(self, image):
        """
        프레임 처리 및 모터 제어
        
        Args:
            image: 처리할 프레임
        """
        if image is None:
            return

        # 이미지 및 edge 값 전처리
        preprocessed_image, edge_tensor = self.preprocess(image, self.edge_value)

        # 모델 추론 및 제어값 계산
        xy = self._get_model_output(preprocessed_image, edge_tensor)
        if xy is None:
            return

        # 모터 제어값 계산 및 적용
        self._apply_motor_control(xy)

    def _get_model_output(self, preprocessed_image, edge_tensor):
        """
        모델 추론 수행
        
        Args:
            preprocessed_image: 전처리된 이미지
            edge_tensor: 전처리된 edge value
            
        Returns:
            numpy.ndarray: 모델 출력값 또는 None
        """
        with torch.no_grad():
            output = self.model(preprocessed_image, edge_tensor)
        xy = output.detach().float().cpu().numpy().flatten()
        
        return xy if xy.size >= 2 else None

    def _apply_motor_control(self, xy):
        """
        모델 출력값을 기반으로 모터 제어
        
        Args:
            xy: 모델 출력값 (x, y 좌표)
        """
        x = xy[0]
        y = (0.5 - xy[1]) / 2.0

        # 조향각 계산
        angle = np.arctan2(x, y)
        pid = angle * self.steering_gain + (angle - self.angle_last) * self.steering_dgain
        self.angle_last = angle
        steering = pid + self.steering_bias

        # 좌/우 모터 속도 계산 및 적용
        motor_speeds = self._calculate_motor_speeds(steering)
        self._apply_motor_speeds(*motor_speeds)

    def _calculate_motor_speeds(self, steering):
        """
        조향각을 기반으로 좌/우 모터 속도 계산
        
        Args:
            steering: 조향각
            
        Returns:
            tuple: (왼쪽 모터 속도, 오른쪽 모터 속도)
        """
        left_motor = max(min(self.speed_gain + steering, 1.0), -0.5)
        right_motor = max(min(self.speed_gain - steering, 1.0), -0.5)
        
        return left_motor, right_motor

    def _apply_motor_speeds(self, left_motor, right_motor):
        """
        계산된 속도를 모터에 적용
        
        Args:
            left_motor: 왼쪽 모터 속도
            right_motor: 오른쪽 모터 속도
        """
        self.robot.motor(left_motor, right_motor)

    def start(self):
        """라인트레이싱 시작"""
        self.running = True
        app_logger.info("Line tracing started")

    def stop(self):
        """라인트레이싱 중지 및 모터 정지"""
        self.running = False
        self.speed_gain = 0
        self.steering_gain = 0
        self.robot.stop()
        app_logger.info("Line tracing stopped")