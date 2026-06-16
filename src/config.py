"""Конфигурация для реального WB API"""
import os
from pathlib import Path


class Config:
    # WB API Token (получить в личном кабинете продавца)
    WB_API_TOKEN = os.getenv("WB_API_TOKEN", "")
    
    # Режим работы: "mock" или "real"
    API_MODE = os.getenv("API_MODE", "mock")
    
    # Базовая директория
    BASE_DIR = Path(__file__).parent.parent
    
    # Порт сервера
    PORT = int(os.getenv("PORT", "8090"))
    HOST = os.getenv("HOST", "127.0.0.1")
    
    @classmethod
    def is_real_api(cls):
        return cls.API_MODE == "real" and cls.WB_API_TOKEN
    
    @classmethod
    def get_token(cls):
        return cls.WB_API_TOKEN