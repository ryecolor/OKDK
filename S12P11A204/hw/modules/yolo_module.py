import cv2
from ultralytics import YOLO
from .logger import app_logger

class YOLODetector:
    def __init__(self, model_path="./models/yolo.pt", min_bbox_ratio=0.50):
        """
        :param model_path: YOLO 모델 파일 경로
        :param min_bbox_ratio: 전체 이미지 대비 최소 바운딩 박스 비율
        """
        self.model = YOLO(model_path)
        self.min_bbox_ratio = min_bbox_ratio
        app_logger.debug("YOLO Model is loading...")
        
    def process_frame(self, frame):
        """
        입력 이미지에서 객체를 탐지하고 정보를 반환합니다.
        :param frame: CV2 이미지 (numpy array)
        :return: (detection_info, detected_frame)
            - detection_info: 탐지된 객체 정보 (바운딩 박스, 클래스 등)
            - detected_frame: 바운딩 박스가 그려진 이미지
        """
        if frame is None:
            return None
                
        results = self.model(frame, verbose=False)
        detection_info = None

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls_id = int(box.cls[0].cpu().numpy())
                conf = float(box.conf[0].cpu().numpy())
                if cls_id > 0 or conf < 0.9:
                    continue
                class_name = r.names[cls_id]
                

                # 바운딩 박스 면적 비율 계산
                frame_area = frame.shape[0] * frame.shape[1]
                bbox_area = (x2 - x1) * (y2 - y1)
                
                if bbox_area >= frame_area * self.min_bbox_ratio:
                    # 탐지 정보 저장
                    detection_info = {
                        "bbox": (x1, y1, x2, y2),
                        "class": class_name,
                        "confidence": conf
                    }
                    break

        return detection_info
