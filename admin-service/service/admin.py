import base64, io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from matplotlibi import pyplot as plt
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import bcrypt

from service.database import engine, SessionLocal, Base
from models.admin import Admin

app = FastAPI()

# 통계 그래프
def save_graph_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    return f"data:image/png;base64,{graph_url}"

def init_db():
    Base.metadata.create_all(bind=engine)

def create_default_admin():
    db = SessionLocal()
    try:
        print("Attempting to create default admin account...")
        # 기본 Admin 계정이 있는지 확인
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
        db.rollbacik()
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise HTTPException(status_code=500, detail="데이터베이스 연결 오류")
    finally:
        db.close()
