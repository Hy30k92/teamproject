from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime

from enum import Enum as PyEnum
import pytz
from service.database import Base

KST = pytz.timezone('Asia/Seoul')

class Status(PyEnum):
    PENDING = "PENDING"  # 대기 중
    APPROVED = "APPROVED"  # 승인됨
    REJECTED = "REJECTED"  # 거부됨
    EXIT = "EXIT"  # 퇴입

class User(Base):
    __tablename__ = 'users'
    uno = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    aname = Column(String(50), nullable=True)
    job = Column(String(100), nullable=True)
    ob = Column(String(100), nullable=True)
    status = Column(Enum(Status), default=Status.PENDING)
    token = Column(String(100), unique=True, index=True)
    regdate = Column(DateTime, default=lambda: datetime.now(KST).replace(microsecond=0))

    def to_dict(self):
        return {
            "uno": self.uno,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "aname": self.aname,
            "job": self.job,
            "ob": self.ob,
            "status": self.status,
            "regdate": self.regdate
        }


class Admin(Base):
    __tablename__ = 'admins'
    ano = Column(Integer, primary_key=True, index=True, autoincrement=True)
    aname = Column(String(50), nullable=False)
    id = Column(String(50), nullable=False, unique=True)
    passwd = Column(String(50), nullable=False)

class EntryExitLog(Base):
    __tablename__ = 'entry_exit_logs'
    no = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    aname = Column(String(50), nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    entry_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    exit_time = Column(DateTime, nullable=True)
