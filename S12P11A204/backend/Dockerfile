FROM python:3.9

WORKDIR /app

# 필요한 패키지 설치
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0\
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# 백그라운드 태스크와 웹서버 함께 실행
CMD ["sh", "-c", "python manage.py migrate && (python manage.py process_tasks --sleep=3600 --log-std) && daphne -b 0.0.0.0 -p 8000 OKDK.asgi:application"]
