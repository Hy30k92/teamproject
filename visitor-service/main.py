from http.client import HTTPException

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates

from routes.visitor import visitor_route
from service import database

app = FastAPI()

templates = Jinja2Templates(directory="frontend/public/views")
# Jinja2 템플릿 설정
origins = [
    "http://localhost:3000", # 허용할 프론트엔드 도메인
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

app.include_router(visitor_route, prefix="/visitor")

@app.on_event("startup")
def on_startup():
    database.init_db()

@app.get("/", response_class=HTMLResponse)
async def read_main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', port=8050, reload=True)
