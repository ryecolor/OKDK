import torch
import torchvision.models as models
from modules.logger import app_logger

class ModifiedResNet(torch.nn.Module):
    """
    경로 정보를 포함하는 수정된 ResNet 모델
    """
    
    def __init__(self):
        """
        ModifiedResNet 초기화
        - ResNet18 기본 모델 로드
        - 입력 채널 수정 (3->4, 경로 정보 추가)
        - 출력 레이어 수정 (2개 출력: x, y)
        """
        super(ModifiedResNet, self).__init__()
        self.resnet = models.resnet18(pretrained=False)
        
        # 입력 채널 3 -> 4로 변경 (추가 채널: 경로 정보)
        self.initial_layer = torch.nn.Conv2d(
            4, 64, 
            kernel_size=7, 
            stride=2, 
            padding=3, 
            bias=False
        )
        
        # 기존 가중치를 복사하고, 새로운 채널은 0으로 초기화
        self._initialize_weights()
        
        # 모델 구조 수정
        self.resnet.conv1 = self.initial_layer
        self.resnet.fc = torch.nn.Linear(512, 2)
        
        app_logger.debug("ResNet is loading...")

    def _initialize_weights(self):
        """가중치 초기화: 기존 채널 복사 및 새 채널 0으로 초기화"""
        with torch.no_grad():
            self.initial_layer.weight[:, :3] = self.resnet.conv1.weight
            self.initial_layer.weight[:, 3] = 0

    def forward(self, image, path_num):
        """
        순전파 연산 수행
        
        Args:
            image (torch.Tensor): 입력 이미지
            path_num (torch.Tensor): 경로 번호
            
        Returns:
            torch.Tensor: 모델의 출력값
        """
        batch_size = image.size(0)
        
        # path_num을 동일한 크기의 채널로 확장하여 image와 결합
        path_channel = path_num.view(batch_size, 1, 1, 1).expand(
            -1, 1, image.size(2), image.size(3)
        )
        x = torch.cat([image, path_channel], dim=1)
        
        return self.resnet(x)

    def load_model(self):
        """저장된 모델 가중치 로드"""
        self.load_state_dict(torch.load('./models/best_steering_model_xy_test_edge4.pth'))
        return self

    def prepare_model(self):
        """
        모델을 추론을 위해 준비
        - GPU로 이동
        - 평가 모드로 설정
        - half precision으로 변환
        """
        device = torch.device('cuda')
        self = self.to(device)
        self = self.eval().half()
        return self