# 🚀 HW 로봇 동작 시스템

이 프로젝트는 **로봇의 동작을 제어하는 시스템**으로, **외부 명령 수신, 상태 전이, 로깅** 등의 기능을 포함하여 로봇을 효율적으로 관리합니다.  
아래 문서는 **각 모듈과 모델의 역할 및 동작 과정**을 설명합니다.

---

## 📂 폴더 구조
```
HW:.
│  📜 main.py
│  📜 readme.md
│  📜 requirements.txt
│
├─📁 models
│      📄 best_steering_model_xy_test_edge4.pth
│      📄 mobilenetv2_finetuned.pth
│      📄 yolo.pt
│      📄 yolo_old.pt
│
└─📁 modules
        📝 config.py
        📝 controller.py
        📝 linetrace.py
        📝 logger.py
        📝 mobile_net_module.py
        📝 motor.py
        📝 pathconvert.py
        📝 recv_command.py
        📝 resnet_model.py
        📝 restful.py
        📝 websocket.py
        📝 yolo_module.py
        📝 __init__.py
```

---

## 📝 파일 설명

### 🎯 **main.py (메인 엔트리 포인트)**
- 🔹 **역할**: 프로그램의 메인 실행 파일로, 로봇의 전체 동작을 제어합니다.
- 🛠 **주요 기능**:
  - ✅ **외부 명령 수신**: `CommandListener`가 웹소켓을 통해 외부 명령을 수신.
  - ✅ **명령 큐 관리**: 스레드 안전한 `Queue`를 이용하여 수신된 명령을 저장.
  - ✅ **상태 전이(FSM) 구성**: `RobotController`의 상태를 `transitions.Machine`을 사용해 정의.
  - ✅ **명령 실행**: 로봇의 상태(`idle`, `active`, `off`)에 따라 적절한 동작 수행.
  - ✅ **안전한 종료**: `shutdown` 명령 수신 시 자원을 정리하며 종료.

---

### ⚙️ **modules 폴더 내 주요 파일**
| 파일명 | 역할 | 주요 기능 |
|--------|--------------------------|---------------------------------------------|
| **config.py** | 변수 관리 모듈 | URL 등 환경변수 및 파일 형식 지정 |
| **controller.py** | 로봇 동작 상태 관리 | 상태 전이 정의, 리소스 로드, 명령 실행 |
| **linetrace.py** | Resnet 모터 제어 모듈듈 | 라인 트레이싱으 모터 조향 코드 |
| **logger.py** | 로깅 기능 제공 | `app_logger`를 이용한 이벤트 기록 |
| **mobile_net_module.py** | 배수구 상태 인식 | Crop된 이미지 Classification |
| **motor.py** | 모터 제어 모듈 | 모터 드라이버 클래스 코드 |
| **pathconvert.py** | 경로 계산 모듈 | 입력 노드로 경로 계산 |
| **recv_command.py** | 명령 수신 모듈 | 웹소켓 명령 수신 및 콜백 처리 |
| **resnet_model.py** | 도로 인식 모듈 | Resnet을 이용한 자율 주행 모델 객체 모듈 |
| **restful.py** | restful 로그 전송 모듈 | restful을 이용한 로그 및 노드 정보 전송 |
| **websocket.py** | 실시간 스트림 모듈 | Websocket을 이용한 실시간 영상전송 모듈 |
| **yolo_module.py** | 배수구 인식 yolo 모델델 | YOLO v8 nano를 이용한 detection 모듈 |

---

### 📦 **models 폴더 내 주요 파일**
| 파일명 | 역할 |
|--------|------------------------------------------------|
| **best_steering_model_xy_test_edge4.pth** | 자율 주행 Resnet 모델델 |
| **mobilenetv2_finetuned.pth** | 배수구 상태 파악용 finetuned MobileNet V2 |
| **yolo.pt** | 배수구 detection용 YOLO v8 nano model |

---

## 🔄 동작 흐름

1️⃣ **프로그램 시작**  
   `main.py` 실행 → `CommandListener`가 외부 명령을 받기 시작.

2️⃣ **명령 큐 생성**  
   스레드 안전한 `Queue`를 생성하여 명령 저장 및 대기.

3️⃣ **상태 전이(FSM) 초기화**  
   `RobotController`와 `transitions.Machine`을 사용해 상태 전이 구성.
   ```
   [loading] -- load() --> [idle]
   [idle] -- activate() --> [active]
   [active] -- deactivate() --> [idle]
   [*] -- shutdown() --> [off]
   ```

4️⃣ **명령 수신 및 처리**  
   외부 명령 수신 → `command_callback` 실행 → 큐에 저장 → `RobotController`가 상태별 동작 수행.

5️⃣ **안전한 종료**  
   `shutdown` 명령 수신 또는 KeyboardInterrupt 발생 시 종료.

---

## 📊 상태 전이 다이어그램
```plaintext
[loading] -- load() --> [idle]
[idle] -- activate() --> [active]
[active] -- deactivate() --> [idle]
[*] -- shutdown() --> [off]
```

