import base64
import io

from fastapi import Form, Depends, APIRouter
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from matplotlib import pyplot as plt
from starlette import status
from starlette.requests import Request
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from fastapi import HTTPException
from datetime import datetime
from service import database
from models.admin import User, Admin, EntryExitLog, Status
from service.database import get_db
from service.email import send_approval_email

admin_route = APIRouter()
templates = Jinja2Templates(directory="public/views")

status_translations = {
    "PENDING": "대기 중",
    "APPROVED": "승인됨",
    "REJECTED": "거절됨",
    "EXIT": "퇴입 완료"
}

@admin_route.post("/admin-login")
async def admin_login(username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    admin = db.query(Admin).filter(Admin.id == username).first()
    if not admin:
        print("Admin not found in database.")
        return JSONResponse(content={"success": False, "message": "로그인 실패: 아이디 또는 비밀번호가 잘못되었습니다."}, status_code=401)

    print(f"Admin found: {admin.id}")

    if bcrypt.checkpw(password.encode('utf-8'), admin.passwd.encode('utf-8')):
        print("Password match.")
        return JSONResponse(content={"success": True, "message": "로그인 성공", "redirect_url": "/admin-dashboard"}, status_code=200)

    print("Password does not match.")
    return JSONResponse(content={"success": False, "message": "로그인 실패: 아이디 또는 비밀번호가 잘못되었습니다."}, status_code=401)

@admin_route.post("/create-default-admin")
async def create_default_admin(db: Session = Depends(get_db)):
    try:
        existing_admin = db.query(Admin).filter(Admin.id == "admin").first()
        if not existing_admin:
            hashed_password = bcrypt.hashpw("admin".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            new_admin = Admin(aname="관리자", id="admin", passwd=hashed_password)
            db.add(new_admin)
            db.commit()
            print("기본 Admin 계정이 생성되었습니다.")
            return JSONResponse(content={"success": True, "message": "기본 Admin 계정이 생성되었습니다."}, status_code=201)
        else:
            print("기본 Admin 계정이 이미 존재합니다.")
            return JSONResponse(content={"success": False, "message": "기본 Admin 계정이 이미 존재합니다."}, status_code=400)
    except IntegrityError as e:
        print(f"Admin 계정 생성 중 문제가 발생했습니다: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Admin 계정 생성 중 문제가 발생했습니다.")
    finally:
        db.close()

@admin_route.get("/admin-dashboard")
async def admin_dashboard(db: Session = Depends(get_db)):
    try:
        # 대기 중인 방문자 데이터를 데이터베이스에서 조회
        pending_visitors = db.query(User).filter(User.status == Status.PENDING).all()
        translated_visitors = [
            {
                "uno": visitor.uno,
                "name": visitor.name,
                "email": visitor.email,
                "phone": visitor.phone,
                "regdate": visitor.regdate.strftime('%Y-%m-%d %H:%M:%S') if visitor.regdate else '등록된 시간이 없습니다.',
                "ob": visitor.ob,
                "translated_status": status_translations.get(visitor.status.value, visitor.status.value)
            }
            for visitor in pending_visitors
        ]

        # JSON 응답으로 반환
        return {"pending_visitors": translated_visitors}

    except Exception as error:
        print(f"Error fetching pending visitors: {error}")
        raise HTTPException(status_code=500, detail="서버 오류 발생")

@admin_route.get("/visitor-list", response_class=JSONResponse)
async def visitor_list(request: Request, db: Session = Depends(get_db)):
    try:
        visitors = db.query(User).all()
        translated_visitors = [
            {
                "uno": visitor.uno,
                "name": visitor.name,
                "email": visitor.email,
                "phone": visitor.phone,
                "ob": visitor.ob,
                "regdate": visitor.regdate.strftime('%Y-%m-%d %H:%M:%S') if visitor.regdate else '등록된 시간이 없습니다.',
                "status": visitor.status.value
            }
            for visitor in visitors
        ]

        return templates.TemplateResponse("visitor_list.ejs", {"request": request, "visitors": translated_visitors})
    except Exception as error:
        print(f"Error fetching visitor data: {error}")
        raise HTTPException(status_code=500, detail="서버 오류 발생")


@admin_route.get("/statistics")
async def statistics_page(db: Session = Depends(get_db)):
    logs = db.query(EntryExitLog).all()

    # 통계 계산
    total_visitors = len(logs)
    total_duration = sum(
        (log.exit_time - log.entry_time).total_seconds() / 60
        for log in logs if log.entry_time and log.exit_time
    )
    avg_visit_duration = total_duration / total_visitors if total_visitors > 0 else 0

    # 요일별 방문자 수
    weekday_visitors = [0] * 7
    for log in logs:
        weekday_visitors[log.entry_time.weekday()] += 1

    # 시간대별 방문자 수
    hour_visitors = [0] * 24
    for log in logs:
        hour_visitors[log.entry_time.hour] += 1

    # 그래프 생성 함수
    def save_graph_to_base64(fig):
        img = io.BytesIO()
        fig.savefig(img, format='png')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close(fig)
        return graph_url

    # 요일별 방문자 수 그래프
    fig, ax = plt.subplots()
    ax.bar(['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'], weekday_visitors)
    weekday_graph = save_graph_to_base64(fig)

    # 시간대별 방문자 수 그래프
    fig, ax = plt.subplots()
    ax.bar(list(range(24)), hour_visitors)
    hour_graph = save_graph_to_base64(fig)

    # JSON 형태로 응답
    return {
        "total_visitors": total_visitors,
        "avg_visit_duration": avg_visit_duration,
        "weekday_graph": f"data:image/png;base64,{weekday_graph}",
        "hour_graph": f"data:image/png;base64,{hour_graph}"
    }

@admin_route.post("/exit/{visitor_id}")
async def log_exit(visitor_id: int, db: Session = Depends(get_db)):
    visitor = db.query(User).filter(User.uno == visitor_id).first()
    if not visitor:
        raise HTTPException(status_code=404, detail="방문자를 찾을 수 없습니다.")

    admin = db.query(Admin).filter(Admin.ano == 1).first()
    if not admin:
        raise HTTPException(status_code=404, detail="관리자를 찾을 수 없습니다.")

    new_log = EntryExitLog(
        name=visitor.name,
        aname=admin.aname,
        createdAt=datetime.now(),
        entry_time=visitor.regdate,
        exit_time=datetime.now()
    )
    db.add(new_log)
    db.commit()

    visitor.status = Status.EXIT
    db.commit()

    return JSONResponse(content={"success": True, "message": "퇴입 완료!"})


@admin_route.post("/admin-approve/{visitor_id}", response_class=JSONResponse)
async def approve_visitor(visitor_id: int, db: Session = Depends(get_db)):
    try:
        visitor = db.query(User).filter(User.uno == visitor_id).first()
        if not visitor:
            return JSONResponse(content={"success": False, "message": "방문자를 찾을 수 없습니다."}, status_code=404)

        visitor.status = Status.APPROVED
        db.commit()

        subject = "방문 신청 승인 완료"
        body = f"안녕하세요, {visitor.name}님.\n\n귀하의 방문 신청이 승인되었습니다. 방문 날짜에 맞춰 방문해주시기 바랍니다.\n\n감사합니다."
        send_approval_email(visitor.email, subject, body)

        return JSONResponse(content={"success": True, "message": f"방문자 {visitor.uno}이 승인되었습니다."})
    except Exception as e:
        print(f"Error approving visitor: {e}")
        return JSONResponse(content={"success": False, "message": f"서버 오류 발생: {str(e)}"}, status_code=500)

@admin_route.post("/admin-reject/{visitor_id}")
async def admin_reject(visitor_id: int, db: Session = Depends(get_db)):
    try:
        visitor = db.query(User).filter(User.uno == visitor_id).first()
        if not visitor:
            return JSONResponse(content={"success": False, "message": "방문자를 찾을 수 없습니다."}, status_code=status.HTTP_404_NOT_FOUND)

        visitor.status = Status.REJECTED
        db.commit()

        subject = "방문 신청 거절 안내"
        body = f"안녕하세요, {visitor.name}님.\n\n귀하의 방문 신청이 거절되었습니다. 자세한 내용은 담당자에게 문의하시기 바랍니다.\n\n감사합니다."
        send_approval_email(visitor.email, subject, body)

        return JSONResponse(content={"success": True, "message": f"방문자 {visitor.uno}이 거절되었습니다."})
    except Exception as e:
        print(f"Error rejecting visitor: {e}")
        return JSONResponse(content={"success": False, "message": f"서버 오류 발생: {str(e)}"}, status_code=500)


