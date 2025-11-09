"""API v1 Routes"""
from fastapi import APIRouter
from app.api.v1 import auth, chat, admin, rag, telegram

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(admin.router, prefix="/admin", tags=["admin"])
router.include_router(rag.router, prefix="/rag", tags=["rag"])
router.include_router(telegram.router, prefix="/telegram", tags=["telegram"])
