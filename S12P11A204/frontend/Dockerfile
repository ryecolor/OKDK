# 빌드 단계
FROM node:14-alpine as build

WORKDIR /app

# package.json과 package-lock.json을 복사합니다.
COPY package.json package-lock.json ./

# 의존성 설치 (OpenLayers 포함)
RUN npm install

# 나머지 소스 코드를 복사합니다.
COPY . .

# 프로덕션을 위한 빌드
RUN npm run build

# 프로덕션 환경
FROM nginx:alpine

# 빌드된 파일을 Nginx 서버로 복사
COPY --from=build /app/build /usr/share/nginx/html

# 포트 80 노출
EXPOSE 80

# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]

# 개발 환경
FROM node:14-alpine as development

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm install
RUN npm install --save-dev webpack webpack-cli webpack-dev-server
RUN npm install --save-dev http-proxy-middleware
RUN npm install gsap @gsap/react

COPY . .

ENV WATCHPACK_POLLING=true
ENV CHOKIDAR_USEPOLLING=true
ENV NODE_ENV=development
ENV NODE_OPTIONS="--max-old-space-size=4096"

# React 개발 서버 포트 노출
EXPOSE 3000

# 개발 서버 실행
CMD ["npm", "start"]
