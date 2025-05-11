# **GitLab 소스 클론 이후 빌드 및 배포 가이드**

## **1. 프로젝트 개요**

본 프로젝트는 `frontend`, `backend`, `hardware`로 구성되어 있으며,\
`frontend`와 `backend`는 **Amazon EC2 환경에서 Docker를 이용하여 배포**됩니다.

## **2. 환경 정보**

- **서버 환경**: Amazon EC2 (Ubuntu 20.04 / AWS Linux 등)
- **컨테이너 관리**: `docker-compose.yml` 사용
- **URL**: 사용자가 설정할 배포 서버의 URL 입력 필요
- **프로그래밍 언어 및 프레임워크**
  - `frontend`: React 18.2.0 (Node.js 18+)
  - `backend`: Django 5.1.5, PostgreSQL 17.2, AWS S3
  - `hardware`: Jetson Orin Nano, JetPack 5.1.3, Python 3.8.7, PyTorch 2.1.0
- **AI 모델**: ResNet18, YOLOv8, MobileNetv2
- **포트 설정**:
  - `frontend`: 3000번 (Docker에서 80번으로 매핑됨)
  - `backend`: 8000번

## **3. 프로젝트 클론 및 환경 변수 설정**

서버에서 프로젝트를 가져오고, 환경 변수를 설정합니다.

```bash
# GitLab에서 프로젝트 클론
git clone https://lab.ssafy.com/s12-webmobile3-sub1/S12P11A204.git
cd project
```

### **📌 서버에 업로드할 폴더**

- `frontend` 및 `backend` 폴더만 업로드합니다.
- `hardware` 폴더는 업로드할 필요 없음.

```bash
scp -r frontend backend user@your-server-url:/home/ubuntu/project
```

### **📌 환경 변수 설정 (`.env`)**

- `backend/OKDK/.env` 파일을 추가해야 합니다.

| 변수명                      | 설명           |
| ------------------------ | ------------ |
| SECRET\_KEY              | 사용자가 발급하여 사용 |
| DB\_NAME                 | `postgres`   |
| DB\_USER                 | `postgres`   |
| DB\_PASSWORD             | `postgres`   |
| DB\_HOST                 | `localhost`  |
| DB\_PORT                 | `5432`       |
| AWS\_ACCESS\_KEY\_ID     | 사용자가 발급하여 사용 |
| AWS\_SECRET\_ACCESS\_KEY | 사용자가 발급하여 사용 |
| WEATHER\_API\_KEY        | 사용자가 발급하여 사용 |
| MAPBOX\_ACCESS\_TOKEN    | 사용자가 발급하여 사용 |

#### **예제 `.env` 파일**

```ini
SECRET_KEY=your-secret-key
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
WEATHER_API_KEY=your-weather-api-key
MAPBOX_ACCESS_TOKEN=your-mapbox-token
```

### **📌 Hardware 환경 변수 설정**

- `hw/modules/config.py` 파일에서 `BASE_URL`을 백엔드 서버 주소와 포트로 설정해야 합니다.(기본 8000번)

#### **예제 `config.py` 파일**

```python
BASE_URL = "http://your-backend-url:8000"
```



## **9. ERD 관련 주요 내용**

### **1) 사용자 및 인증**
| 테이블명 | 필드명 | 설명 |
|----------|--------|------|
| **accounts_customer** | `id` | 사용자 고유 ID |
|  | `username` | 사용자 이름 |
|  | `email` | 이메일 주소 |
|  | `password` | 비밀번호 해시값 |
|  | `is_superuser` | 관리자 여부 |
|  | `is_staff` | 스태프 여부 |
|  | `is_active` | 계정 활성 상태 |
|  | `date_joined` | 가입 날짜 |
|  | `district_id` | 사용자와 연결된 지역 ID |
| **token_blacklist_blacklistedtoken** | `id` | 블랙리스트된 토큰 정보 |
| **token_blacklist_outstandingtoken** | `id` | 만료되지 않은 토큰 목록 |

### **2) 지역 및 환경 정보**
| 테이블명 | 필드명 | 설명 |
|----------|--------|------|
| **region_block** | `id` | 지역 블록 정보 |
|  | `Cumulative_state_score` | 침수 위험 수치 |
|  | `Flooding_sensitivity` | 감지 민감도 |
| **region_district** | `id` | 지역 구분 정보 |
| **drain_drain** | `id` | 배수구 위치 및 상태 정보 |
| **drain_drainrepair** | `id` | 배수구 수리 내역 |

### **3) 로봇 관련 정보**
| 테이블명 | 필드명 | 설명 |
|----------|--------|------|
| **robot_info_robot** | `id` | 로봇 상태 및 작동 가능 여부 |
|  | `selected_drain` | 선택된 배수구 |
|  | `is_robot_available` | 로봇 사용 가능 여부 |
| **robot_info_rebotlog** | `id` | 로봇의 작업 로그 |
| **robot_info_logentry** | `id` | 로봇의 센서 데이터 로그 |

### **4) 백그라운드 작업 및 설정**
| 테이블명 | 필드명 | 설명 |
|----------|--------|------|
| **background_task** | `id` | 비동기 작업을 위한 테스크 정보 |
| **background_task_completedtask** | `id` | 완료된 비동기 작업 기록 |
| **map_config_mapconfig** | `id` | 지도 설정 및 레이어 정보 |
| **map_config_legenditem** | `id` | 지도 범례 정보 |
| **video_video** | `id` | 저장된 영상 데이터 |

## **5. Docker 빌드 및 실행**

Docker를 이용해 서비스를 빌드하고 실행합니다.

```bash
# docker-compose를 이용한 빌드 및 실행
docker-compose up --build -d
```

## **6. 배포 및 실행 확인**

배포 후 각 서비스가 정상 실행되는지 확인합니다.

### **✔ Docker 컨테이너 상태 확인**

```bash
docker ps
```

### **✔ Backend API 응답 확인**

```bash
curl http://your-server-url:8000/health/
```

### **✔ Frontend 접근 확인**

웹 브라우저에서 `http://your-server-url` 접속 (포트 80 → 프론트엔드 3000번 포트와 매핑됨)

## **7. 배포 시 주의사항**

- `.env` 파일이 누락되지 않도록 확인하세요.
- EC2 방화벽 설정에서 **포트(80, 443, 8000번 API 포트 등)를 허용**해야 합니다.
- Docker 빌드 후 `docker logs` 명령어로 로그를 확인하세요.

## **8. 추가적인 설정**

- AWS EC2 인스턴스에서 실행될 경우 **보안 그룹 설정**을 통해 HTTP/HTTPS를 열어야 합니다.
- 필요시 **SSL 인증서(HTTPS)** 적용을 고려해야 합니다.
