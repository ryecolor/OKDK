import os
import threading
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import mobilenet_v2 #Mobilenet_V2_Weights
from torchvision import models, transforms
import cv2
from .logger import app_logger 

class MobileNetClassifier:
    def __init__(self, model_path="./models/mobilenetv2_finetuned.pth", margin=40):
        """
        :param model_path: MobileNet 모델 파일 경로
        :param margin: crop 시 바운딩 박스 주변 여백 (픽셀)
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.classes = ["bad", "good", "medium"]
        self.num_classes = len(self.classes)
        self.model = self._load_model(model_path)
        self.margin = margin
        
        self.preprocess = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])

    def _load_model(self, model_path):
        """
        모델을 로드하는 작업을 하는 method
        :param model_path: model이 위치한 주소
        :return model: load한 eval 상태 model 객체
        """ 
        model = models.mobilenet_v2(weights=None)
        model.classifier[1] = nn.Linear(model.last_channel, self.num_classes)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {model_path}")

        model.load_state_dict(torch.load(model_path, map_location=self.device))
        model.to(self.device)
        model.eval()
        app_logger.debug("MobilNet is loading...")
        return model

    def crop_image(self, image, detection_info):
        """
        탐지 정보를 바탕으로 이미지를 crop합니다.
        :param image: 원본 이미지
        :param detection_info: YOLO에서 반환된 탐지 정보
        :return: crop된 이미지
        """
        if detection_info is None:
            return None
            
        x1, y1, x2, y2 = detection_info["bbox"]
        return image[y1:y2, x1:x2]

    def predict(self, image_array):
        """
        이미지를 분류합니다.
        :param image_array: CV2 이미지 (numpy array)
        :return: (predicted_class, confidence) 예측된 클래스와 확률 or (None, 0.0)
        """
        if image_array is None:
            return None, 0.0
            
        try:
            image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            image_pil = Image.fromarray(image_rgb)
        except Exception as e:
            app_logger.error(f"이미지 변환 실패: {e}")
            return None, 0.0

        input_tensor = self.preprocess(image_pil).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = F.softmax(outputs, dim=1)
            max_prob, pred = torch.max(probabilities, 1)

        predicted_class = self.classes[pred.item()]
        confidence = max_prob.item()

        return predicted_class, confidence

    def draw_result(self, image, detection_info, result, confidence):
        """
        MobileNet으로 분류한 결과를 이미지에 그립니다.
        :param image: 원본 이미지
        :param detection_info: YOLO 탐지 정보
        :param result: 예측된 클래스
        :param confidence: 예측 확률
        :return: 결과가 그려진 이미지(image)
        """
        if detection_info is None or result is None:
            return image

        text = result
        conf = f"{confidence:.2f}"
        x1, y1, x2, y2 = detection_info["bbox"]

        # 컬러 설정 
        color = {
            "good": (0, 255, 0), # green color 
            "medium": (0, 255, 255), # yellow color
            "bad": (0, 0, 255) # red color
        }.get(result, (128, 128, 128))

        # 텍스트 관련 설정
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        thickness = 2
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)

        # 텍스트 위치 계산 (중앙 정렬)
        center_x = x1 + (x2 - x1) // 2
        center_y = y1 + (y2 - y1) // 2
        text_x = center_x - text_width // 2
        text_y = center_y + text_height // 2

        # 결과 그리기
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, text, (text_x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)
        cv2.putText(image, conf, (x1 + 20, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return image
