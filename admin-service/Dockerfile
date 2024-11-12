# 베이스 이미지로 Python 3.11 사용
FROM python:3.11-slim-bullseye

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 목록을 복사
COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 전체 소스 코드 복사
COPY . .

# FastAPI 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

