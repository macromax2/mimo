"""Мок-сервер Wildberries API"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path
import random

from .data import (
    generate_mock_orders,
    generate_mock_sales,
    generate_mock_finance,
    generate_mock_stocks,
    generate_mock_products,
)

app = FastAPI(title="WB Mock API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mock_token = "test-token-12345"


@app.get("/")
async def root():
    return {"message": "WB Mock API", "status": "running"}


@app.get("/auth")
async def auth():
    """Мок авторизации"""
    return {"access_token": mock_token, "token_type": "bearer"}


@app.get("/api/v5/supplier/orders")
async def get_orders(
    dateFrom: str = Query(None, description="Дата начала"),
    dateTo: str = Query(None, description="Дата окончания"),
    limit: int = Query(100, ge=1, le=1000),
    rrdid: int = Query(0, description="ID последней записи"),
    flag: int = Query(0, description="Флаг пагинации"),
):
    """Мок эндпоинта заказов"""
    orders = generate_mock_orders(limit)
    
    if dateFrom:
        date_from = datetime.fromisoformat(dateFrom.replace("Z", "+00:00"))
        orders = [o for o in orders if datetime.fromisoformat(o["date"]) >= date_from]
    
    return {
        "orders": orders,
        "cursor": {"total": len(orders), "lastChangeDate": datetime.now().isoformat()}
    }


@app.get("/api/v5/supplier/sales")
async def get_sales(
    dateFrom: str = Query(None),
    dateTo: str = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    rrdid: int = Query(0),
    flag: int = Query(0),
):
    """Мок эндпоинта продаж"""
    sales = generate_mock_sales(limit)
    
    if dateFrom:
        date_from = datetime.fromisoformat(dateFrom.replace("Z", "+00:00"))
        sales = [s for s in sales if datetime.fromisoformat(s["rr_dt"]) >= date_from]
    
    return {
        "sales": sales,
        "cursor": {"total": len(sales), "lastChangeDate": datetime.now().isoformat()}
    }


@app.get("/api/v5/supplier/reportDetailByPeriod")
async def get_finance(
    dateFrom: str = Query(None),
    dateTo: str = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    rrdid: int = Query(0),
    flag: int = Query(0),
):
    """Мок эндпоинта финансовых отчётов"""
    finance = generate_mock_finance(30)
    
    if dateFrom:
        date_from = datetime.fromisoformat(dateFrom.replace("Z", "+00:00"))
        finance = [f for f in finance if datetime.fromisoformat(f["date"]) >= date_from]
    
    return {
        "data": finance,
        "cursor": {"total": len(finance), "lastChangeDate": datetime.now().isoformat()}
    }


@app.get("/api/v5/supplier/stocks")
async def get_stocks(
    dateFrom: str = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    rrdid: int = Query(0),
):
    """Мок эндпоинта остатков"""
    stocks = generate_mock_stocks()
    return {
        "stocks": stocks[:limit],
        "cursor": {"total": len(stocks), "lastChangeDate": datetime.now().isoformat()}
    }


@app.get("/api/v5/supplier/products")
async def get_products(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Мок эндпоинта товаров"""
    products = generate_mock_products()
    return {
        "products": products[offset:offset+limit],
        "cursor": {"total": len(products)}
    }


@app.get("/api/v5/supplier/cash-flow")
async def get_cash_flow(
    dateFrom: str = Query(None),
    dateTo: str = Query(None),
):
    """Мок эндпоинта денежных потоков"""
    return {
        "cash_flows": [
            {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "payment_amount": random.randint(50000, 200000),
                "payment_amount_fact": random.randint(50000, 200000),
            }
            for i in range(30)
        ]
    }


FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


@app.get("/app")
async def frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/docs")
async def docs():
    return {"message": "API Documentation", "endpoints": [
        "/api/v5/supplier/orders",
        "/api/v5/supplier/sales",
        "/api/v5/supplier/reportDetailByPeriod",
        "/api/v5/supplier/stocks",
        "/api/v5/supplier/products",
        "/api/v5/supplier/cash-flow",
    ]}