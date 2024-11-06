from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates
from service import database
from routes.admin import admin_route
import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from service.database import engine, Base, SessionLocal 
from models.admin import Admin  
from routes.admin import admin_route

app = FastAPI()
templates = Jinja2Templates(directory="frontend/public/views")

# CORS 설정
origins = [
    "http://localhost:3000",  # 허용할 프론트엔드 도메인
    "http://127.0.0.1:3000",
    "http://13.125.180.195:3000",
    "http://43.201.104.24"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Admin 라우터 추가
app.include_router(admin_route, prefix="/admin")

# 데이터베이스 초기화 함수
def init_db():
    database.Base.metadata.create_all(bind=database.engine)

# 기본 Admin 계정 생성 함수
def create_default_admin():
    db = database.SessionLocal()
    try:
        print("Attempting to create default admin account...")
        # 기본 Admin 계정 존재 여부 확인
        existing_admin = db.query(Admin).filter(Admin.id == "admin").first()
        if not existing_admin:
            hashed_password = bcrypt.hashpw("admin".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            new_admin = Admin(aname="관리자", id="admin", passwd=hashed_password)
            db.add(new_admin)
            db.commit()
            print("기본 Admin 계정이 생성되었습니다.")
        else:
            print("기본 Admin 계정이 이미 존재합니다.")
    except IntegrityError as e:
        print(f"Admin 계정 생성 중 문제가 발생했습니다: {e}")
        db.rollback()
    finally:
        db.close()

# FastAPI 애플리케이션 시작 이벤트
@app.on_event("startup")
def on_startup():
    print("Starting up and initializing database...")
    init_db()  # 데이터베이스 초기화
    create_default_admin()  # 기본 Admin 계정 생성

# 기본 라우트 정의
@app.get("/", response_class=HTMLResponse)
async def read_main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Uvicorn을 통한 애플리케이션 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)

