from fastapi import APIRouter

from src.config import ENVIRONMENT

api_router = APIRouter()


if ENVIRONMENT == "local":
    pass
