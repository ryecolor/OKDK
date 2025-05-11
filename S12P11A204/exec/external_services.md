# **외부 서비스 및 API 키 설정 가이드**

이 문서는 프로젝트에서 사용하는 외부 서비스 및 API 키 발급 방법과 설정 방법을 정리한 것입니다.

---

## **1. 사용 중인 API 키 목록 및 적용 경로**

| API 키 변수명 | 사용 목적 | 적용 경로 |
|-------------|---------|---------|
| `AWS_ACCESS_KEY_ID` | AWS 서비스 인증 (S3, Lambda, EC2 등) | `/backend/OKDK/.env` |
| `AWS_SECRET_ACCESS_KEY` | AWS 서비스 인증 (S3, Lambda, EC2 등) | `/backend/OKDK/.env` |
| `MAPBOX_ACCESS_TOKEN` | Mapbox GL JS를 사용한 지도 렌더링 및 조작 | `/backend/OKDK/.env`, `/backend/map_config/fixtures/inital_data.json` |
| `WEATHER_API_KEY` | 기상청 데이터를 가져오기 위한 API 키 | `/backend/OKDK/.env` |
| `flood_layer_url` | 침수 데이터 API 키를 활용하여 지도에서 침수 데이터를 표시 | `/backend/OKDK/.env` |

---

## **2. API 키 발급 방법**

### **1️⃣ AWS API 키 발급 방법**
- **사용 목적**: AWS 서비스 (S3, Lambda, EC2 등)를 사용하기 위한 인증
- **발급 절차**:
  1. [AWS IAM 콘솔](https://aws.amazon.com/iam/)에 로그인
  2. IAM 사용자 생성 또는 기존 사용자 선택
  3. **액세스 키 (Access Key ID, Secret Access Key) 생성**
  4. 발급된 키를 `/backend/OKDK/.env` 파일에 추가

- **예제 설정 (`.env` 파일)**
```ini
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
```

---

### **2️⃣ Mapbox API 키 발급 방법**
- **사용 목적**: Mapbox GL JS를 이용해 지도 렌더링 및 조작
- **발급 절차**:
  1. [Mapbox 공식 웹사이트](https://www.mapbox.com/)에서 회원가입 및 로그인
  2. **Access Token 생성**
  3. 발급된 키를 `/backend/OKDK/.env`, , `/backend/map_config/fixtures/inital_data.json` 파일에 추가

- **예제 설정 (`.env` 파일)**
```ini
MAPBOX_ACCESS_TOKEN=your-mapbox-access-token
```
```ini
{"access_token": your-mapbox-access-token}
```

---

### **3️⃣ 기상청 API 키 발급 방법**
- **사용 목적**: 날씨 데이터를 조회
- **발급 절차**:
  1. [기상청 데이터 포털](https://data.kma.go.kr/)에 접속
  2. 회원가입 후 로그인
  3. 데이터 활용 신청을 통해 API 키 발급
  4. 발급된 키를 `/backend/OKDK/.env` 파일에 추가

- **예제 설정 (`.env` 파일)**
```ini
WEATHER_API_KEY=your-weather-api-key
```

---

### **4️⃣ 침수 데이터 API 키 발급 방법**
- **사용 목적**: 침수 위험 지도 데이터를 가져와 지도에 오버레이
- **발급 절차**:
  1. [안전지도 포털](https://safemap.go.kr/opna/crtfc/keyAgree.do)에서 API 키 발급
  2. 발급된 키를 `/backend/OKDK/.env` 파일에 추가
  3. API 호출 시, URL 내 `{api_key}` 부분에 발급된 키를 삽입

- **예제 URL 설정 (`.env` 파일)**
```ini
"flood_layer_url": "https://www.safemap.go.kr/openApiService/wms/getLayerData.do?apikey={your-api-key}&LAYERS=A2SM_FLUDMARKS&STYLES=A2SM_FludMarks&FORMAT=image/png&TRANSPARENT=true&VERSION=1.3.0&SERVICE=WMS&REQUEST=GetMap&CRS=EPSG:3857&BBOX={bbox-epsg-3857}&WIDTH=256&HEIGHT=256"
```

## **3. 환경 변수 파일 예제 (`.env`)**
아래는 API 키가 없는 환경 변수 예제 파일입니다. 실제 API 키를 발급받아 입력 후 사용하세요.

```ini
SECRET_KEY=
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
WEATHER_API_KEY=
MAPBOX_ACCESS_TOKEN=
```