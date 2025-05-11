## 📂 폴더 구조

```
frontend  
├── public  
│   ├── favicon.ico  
│   ├── flood_block_1.png  
│   ├── flood_block_2.png  
│   ├── flood_block_3.png  
│   └── ...  
├── src  
│   ├── assets  
│   │   ├── alert-icon.png  
│   │   ├── genesisman.png  
│   │   ├── home-icon.png  
│   │   ├── logo.png  
│   │   └── play-icon.png  
│   ├── components  
│   │   ├── AlertComponent.js  
│   │   ├── BaseMapComponent.js  
│   │   ├── BlockNavbar.js  
│   │   ├── DetailComponent.js  
│   │   ├── DrainageMapComponent.js  
│   │   ├── DrainNavbar.js  
│   │   ├── InfoComponent.js  
│   │   ├── LoadingOverlay.js  
│   │   ├── MapComponent.js  
│   │   └── WeatherComponent.js  
│   ├── styles  
│   │   ├── Alert.css  
│   │   ├── App.css  
│   │   ├── BlockNavbar.css  
│   │   ├── Detail.css  
│   │   ├── DrainageMap.css  
│   │   ├── DrainNavbar.css  
│   │   ├── Info.css  
│   │   ├── LoadingOverlay.css  
│   │   ├── Map.css  
│   │   └── Weather.css  
│   ├── utils  
│   │   └── bezierUtils.js  
│   ├── App.js  
│   ├── App.test.js  
│   ├── AuthContext.js  
│   ├── index.js  
│   ├── reportWebVitals.js  
│   └── setupTests.js  
├── package.json  
├── package-lock.json  
├── Dockerfile  
└── README.md  
```

---

## 📌 폴더 및 파일 설명

### 📁 `public/` *(정적 파일 저장)*

- **`favicon.ico`** : 브라우저 탭 아이콘
- **`flood_block_*.png`** : 침수 이미지

### 📁 `src/` *(소스 코드 폴더)*

#### 📂 `assets/` *(이미지 및 정적 파일)*

- **`alert-icon.png`**, **`logo.png`** 등

#### 📂 `components/` *(UI 컴포넌트)*

- **`AlertComponent.js`** : 알림 표시
- **`BaseMapComponent.js`** : 기본 지도
- **`DrainageMapComponent.js`** : 배수 지도
- **`WeatherComponent.js`** : 날씨 정보
- 기타 여러 UI 요소 포함

#### 📂 `styles/` *(스타일 파일)*

- **`Alert.css`**, **`Map.css`**, **`DrainNavbar.css`** 등

#### 📂 `utils/` *(유틸리티 함수)*

- **`bezierUtils.js`** : 베지어 곡선 관련 유틸 함수

---

## 📌 주요 파일 설명

- **`App.js`** : 애플리케이션의 루트 컴포넌트
- **`index.js`** : 앱 진입점
- **`AuthContext.js`** : 인증 컨텍스트 관리
- **`reportWebVitals.js`** : 웹 성능 측정

---

## 📌 루트 파일들

📦 **프로젝트 설정 및 빌드 관련 파일**

- **`package.json`** : 프로젝트 메타데이터 및 의존성 정보
- **`package-lock.json`** : 의존성 버전 고정 파일
- **`Dockerfile`** : Docker 이미지 빌드를 위한 설정 파일
- **`README.md`** : 프로젝트 설명 파일

---
