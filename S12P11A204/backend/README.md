# 🛠 Backend 기능 설명

## 📌 개요
- **언어**: `Python`
- **프레임워크**: `Django`

## 📂 파일 디렉토리 구조
```plaintext
backend/
├── accounts/ 
├── alerts/
├── connection/
├── drain/
├── map_config/
├── OKDK/
├── region/
├── robot_info/
├── Dockerfile
├── manage.py
└── requirements.txt
```

## 🏗 프로젝트
### 🔹 OKDK
- 메인 프로젝트 기본 정보를 저장

---

## 📌 앱 (Django Apps)

### 🧑‍💻 1. accounts (계정 관리)
- **기능**: `JWT 인증`을 활용한 로그인, 로그아웃, 회원가입, 회원탈퇴 관리  
- **주요 파일**:  
  - `models.py` - 사용자 정보 저장  
  - `views.py` - 로그인 및 인증 처리  

---

### 🔔 2. alerts (알림 시스템)
- **기능**: 특정 이벤트 발생 시 **WebSocket**을 통해 클라이언트에 알림 전송  
- **주요 파일**:
  - `consumers.py` - WebSocket 메시지 JSON 변환 후 전송
  - `models.py` - 외부 공공데이터 API 활용한 정보 저장
  - `signals.py` - 특정 조건 만족 시 WebSocket으로 알림 전송  
    ✅ **조건 예시**:  
    - 날씨 API 호출 시 **눈/비 예보** 발생  
    - 로봇 주행 중 **낙엽·쓰레기 과다**  
    - **로봇 주행 불가능** 상태 감지  
  - `tasks.py` - 1시간마다 API 호출하여 날씨 데이터 업데이트  

---

### 🔄 3. connection (WebSocket 데이터 전송)
- **기능**: **양방향 WebSocket 통신**  
- **주요 파일**:
  - `consumers.py`  
    ✅ 하드웨어 ↔ 서버 ↔ 클라이언트 간 데이터 전송  
    1) 하드웨어 실시간 스트리밍 전송  
    2) 로봇 (비)활성화 명령 전송  
    3) 하드웨어에서 **배수구 사진 수신** 후 클라이언트에 상태 전송  
  - `routing.py` - WebSocket 연결 URL 관리  

---

### 🏞 4. drain (배수구 정보 관리)
- **기능**: 배수구 상태 및 점검 필요 내역 관리  
- **주요 파일**:
  - `models.py` - 배수구 관련 정보 저장  
  - `views.py`  
    ✅ `receive_img()` - 배수구 이미지 **AWS S3**에 저장 후 상태 전송  
    ✅ `state_correction()` - 배수구 상태 변경  

---

### 🗺 5. map_config (지도 설정)
- **기능**: `Mapbox` 연동을 위한 정보 저장  
- **주요 파일**:
  - `models.py` - 지도 API 키, 기본 좌표값 관리  
  - `views.py`  
    ✅ `get_drain_data()` - 특정 블록의 배수구 정보 조회  

---

### 🌍 6. region (지역 정보 관리)
- **기능**: ERD 구조상 `최상위 지역 정보` 관리  
- **주요 파일**:
  - `models.py` - 지역명, 블록, 배수구 종합 점수 저장  
  - `views.py`  
    ✅ `SelectRobotAndDrain()` - 탐색할 배수구 및 로봇 배정  
    ✅ `block_condition()` - 블록 내 배수구 점수 조회  
    ✅ `deactivate_robot()` - 로봇 정지 명령  
    ✅ `get_flood_images()` - 침수 현황 조회  

---

### 🤖 7. robot_info (로봇 정보 관리)
- **기능**: 로봇의 상태 및 수리 이력 관리  
- **주요 파일**:
  - `models.py` - 로봇 정보, 위치, 수리 이력, 하드웨어 로그 저장  
  - `views.py`  
    ✅ `get_robot_info()` - 로봇 정보 조회  
    ✅ `receive_log()` - 하드웨어에서 로그 수신 후 데이터 파싱  
    ✅ `SelectDrain()` - 로봇이 탐색할 배수구 정보 큐 저장  
    ✅ `get_queue()` - 큐에 저장된 배수구 정보 조회  

---

## 🏗 기타 설정

### 🐳 Dockerfile
- 필요한 패키지 설치 후 **웹 서버 및 백그라운드 태스크 실행**  

### 📜 requirements.txt
- 프로젝트에 필요한 **패키지 리스트** 저장  
