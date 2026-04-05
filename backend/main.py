from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os, atexit, logging
from contextlib import asynccontextmanager

from auth.routes import router as auth_router
from api.chat import router as chat_router
from api.history import router as history_router
from api.maps import router as maps_router
from api.documents import router as documents_router
from api.notifications import router as notifications_router
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from scheduler import start_scheduler
        scheduler = start_scheduler()
        atexit.register(lambda: scheduler.shutdown(wait=False))
        logger.info("Scheduler démarré")
    except Exception as e:
        logger.error(f"Erreur scheduler: {e}")
    yield

app = FastAPI(title=settings.APP_NAME, version="3.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://idaraty.vercel.app",
        "https://idaraty-*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(os.path.join(static_dir, "pdfs"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(history_router)
app.include_router(maps_router)
app.include_router(documents_router)
app.include_router(notifications_router)

@app.get("/")
def root():
    return {"message": "iDaraty API", "version": "3.0.0", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}