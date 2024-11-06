import secrets

from fastapi import Form, Depends, APIRouter, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
import logging

from models.visitor import User, Status
from service import database
from service.database import get_db
from service.email import send_notification_email

logging.basicConfig(level=logging.INFO)

visitor_route = APIRouter()
templates = Jinja2Templates(directory="public/views")

@visitor_route.get("/visitor-register", response_class=HTMLResponse)
async def visitor_register_page(request: Request):
    return templates.TemplateResponse("visitor_register.ejs", {"request": request})


@visitor_route.post("/visitor-register")
async def visitor_register(
        name: str = Form(...),
        email: str = Form(...),
        phone: str = Form(...),
        ob: str = Form(...),
        aname: str = Form(...),
        job: str = Form(...),
        db: Session = Depends(database.get_db)
):
    # Create new visitor entry
    new_visitor = User(
        name=name,
        email=email,
        phone=phone,
        ob=ob,
        aname=aname,
        job=job,
        status=Status.PENDING
    )
    db.add(new_visitor)
    db.commit()
    db.refresh(new_visitor)

    token = secrets.token_urlsafe(16)
    new_visitor.token = token
    db.commit()

    approval_link = f"http://13.125.180.195:3000/visitor-detail?token={token}"
    send_notification_email(email, approval_link, token)

    return {"message": "Visitor registered successfully"}

@visitor_route.get("/visitor-dashboard")
async def get_all_visitors(db: Session = Depends(get_db)):
    visitors = db.query(User).all()

    for visitor in visitors:
        visitor.status = visitor.status.value

    return {"visitors": visitors}

@visitor_route.get("/visitor-detail", response_class=HTMLResponse)
async def visitor_detail_by_token(token: str, request: Request, db: Session = Depends(get_db)):
    visitor = db.query(User).filter(User.token == token).first()

    if not visitor:
        raise HTTPException(status_code=404, detail="유효하지 않은 토큰입니다.")

    return templates.TemplateResponse("visitor_detail.ejs", {"request": request, "visitor": visitor})


@visitor_route.post("/exit/{user_id}")
async def log_exit(user_id: int, db: Session = Depends(get_db)):
    visitor = db.query(User).filter(User.uno == user_id).first()

    if not visitor or visitor.status != Status.APPROVED.value:
        return JSONResponse({"success": False, "message": "Visitor not eligible for exit"}, status_code=400)

    visitor.status = Status.EXIT.value
    db.commit()
    return JSONResponse({"success": True, "message": "Visitor exit logged successfully"})


