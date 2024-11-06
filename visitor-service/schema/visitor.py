from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    aname: Optional[str] = None
    job: Optional[str] = None
    ob: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    uno: int

    class Config:
        orm_mode = True


class AdminBase(BaseModel):
    aname: str
    id: str
    passwd: str

class AdminCreate(AdminBase):
    pass

class Admin(AdminBase):
    ano: int

    class Config:
        orm_mode = True


class EntryExitLogBase(BaseModel):
    name: str
    createdAt: datetime
    aname: Optional[str] = None
    entry_time: datetime
    exit_time: Optional[datetime] = None

class EntryExitLogCreate(EntryExitLogBase):
    pass

class EntryExitLog(EntryExitLogBase):
    no: int

    class Config:
        orm_mode = True