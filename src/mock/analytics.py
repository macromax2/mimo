"""Сервер аналитики селлеров"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import random
import json

from .data import (
    generate_mock_orders,
    generate_mock_sales,
    generate_mock_finance,
    generate_mock_stocks,
    generate_mock_products,
)

app = FastAPI(title="Seller Analytics", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Seller Analytics API", "status": "running"}


@app.get("/api/dashboard")
async def dashboard():
    """Главная панель аналитики"""
    products = generate_mock_products()
    orders = generate_mock_orders(100)
    sales = generate_mock_sales(80)
    
    total_revenue = sum(s.get("for_pay", s.get("sale_total", 0)) for s in sales)
    total_orders = len(orders)
    total_cancelled = sum(1 for o in orders if o["isCancel"])
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    avg_rating = sum(p["rating"] for p in products) / len(products)
    total_reviews = sum(p["reviews"] for p in products)
    
    return {
        "summary": {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "total_cancelled": total_cancelled,
            "cancel_rate": round(total_cancelled / total_orders * 100, 2) if total_orders > 0 else 0,
            "avg_order_value": round(avg_order_value, 2),
            "avg_rating": round(avg_rating, 2),
            "total_reviews": total_reviews,
            "active_products": len(products),
        },
        "revenue_trend": [
            {
                "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "revenue": random.randint(30000, 150000),
                "orders": random.randint(10, 50),
            }
            for i in range(30)
        ],
        "top_products": products[:5],
        "recent_orders": orders[:10],
    }


@app.get("/api/products")
async def products():
    """Список товаров"""
    return {"products": generate_mock_products()}


@app.get("/api/products/{nm_id}")
async def product_detail(nm_id: int):
    """Детали товара"""
    products = generate_mock_products()
    product = next((p for p in products if p["nm_id"] == nm_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "product": product,
        "price_history": [
            {
                "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "price": product["price"] + random.randint(-200, 200),
            }
            for i in range(30)
        ],
        "sales_history": [
            {
                "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "orders": random.randint(0, 20),
                "revenue": random.randint(0, 50000),
            }
            for i in range(30)
        ],
        "competitors": [
            {"name": f"Конкурент {i}", "price": product["price"] + random.randint(-500, 500), "rating": round(random.uniform(3.5, 5.0), 1)}
            for i in range(1, 6)
        ],
    }


@app.get("/api/analytics/pnl")
async def pnl_analytics(
    dateFrom: Optional[str] = None,
    dateTo: Optional[str] = None,
):
    """P&L аналитика"""
    finance = generate_mock_finance(30)
    
    total_sales = sum(f["sale_amount"] for f in finance if f["operation_type"] == "Продажа")
    total_fees = sum(f["service_fee"] for f in finance if f["operation_type"] == "Продажа")
    total_storage = sum(abs(f["payment_amount"]) for f in finance if f["operation_type"] == "Хранение")
    total_penalties = sum(f["penalty"] for f in finance if f["operation_type"] == "Штраф")
    total_logistics = sum(random.randint(30, 80) for _ in range(100))
    
    return {
        "summary": {
            "total_revenue": total_sales,
            "total_fees": total_fees,
            "total_storage": total_storage,
            "total_logistics": total_logistics,
            "total_penalties": total_penalties,
            "net_profit": total_sales - total_fees - total_storage - total_logistics - total_penalties,
            "margin": round((total_sales - total_fees - total_storage - total_logistics - total_penalties) / total_sales * 100, 2) if total_sales > 0 else 0,
        },
        "daily_breakdown": [
            {
                "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "revenue": revenue,
                "fees": fees,
                "storage": random.randint(1000, 5000),
                "logistics": random.randint(3000, 8000),
                "profit": revenue - fees - random.randint(3000, 8000) - random.randint(1000, 5000),
            }
            for i in range(30)
            for revenue in [random.randint(50000, 200000)]
            for fees in [int(revenue * random.uniform(0.12, 0.18))]
        ],
        "by_category": [
            {"category": "Электроника", "revenue": total_sales * 0.6, "margin": 15.2},
            {"category": "Аксессуары", "revenue": total_sales * 0.3, "margin": 22.5},
            {"category": "Другое", "revenue": total_sales * 0.1, "margin": 18.0},
        ],
    }


@app.get("/api/analytics/stocks")
async def stocks_analytics():
    """Аналитика остатков"""
    stocks = generate_mock_stocks()
    
    total_stock = sum(s["stock"] for s in stocks)
    total_value = sum(s["stock"] * s["price"] for s in stocks)
    avg_days_without_sales = sum(s["daysWithoutSales"] for s in stocks) / len(stocks) if stocks else 0
    
    low_stock = [s for s in stocks if s["stock"] < 10]
    slow_moving = [s for s in stocks if s["daysWithoutSales"] > 30]
    
    return {
        "summary": {
            "total_stock": total_stock,
            "total_value": total_value,
            "avg_days_without_sales": round(avg_days_without_sales, 1),
            "low_stock_count": len(low_stock),
            "slow_moving_count": len(slow_moving),
        },
        "by_warehouse": [
            {"warehouse": wh, "stock": sum(s["stock"] for s in stocks if s["warehouse_name"] == wh)}
            for wh in set(s["warehouse_name"] for s in stocks)
        ],
        "low_stock": low_stock[:10],
        "slow_moving": slow_moving[:10],
    }


@app.get("/api/analytics/forecast")
async def forecast(
    nm_id: int = Query(None),
    days: int = Query(30, ge=7, le=90),
):
    """Прогноз продаж"""
    products = generate_mock_products()
    
    if nm_id:
        product = next((p for p in products if p["nm_id"] == nm_id), None)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        target_products = [product]
    else:
        target_products = products
    
    forecast_data = []
    for i in range(1, days + 1):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        day_forecast = {
            "date": date,
            "products": []
        }
        
        for product in target_products:
            base_orders = product["orders"] / 30
            predicted_orders = max(0, int(base_orders * random.uniform(0.7, 1.3)))
            
            day_forecast["products"].append({
                "nm_id": product["nm_id"],
                "name": product["name"],
                "predicted_orders": predicted_orders,
                "predicted_revenue": predicted_orders * product["price"],
            })
        
        forecast_data.append(day_forecast)
    
    return {
        "forecast_period": days,
        "forecast": forecast_data,
        "summary": {
            "total_predicted_orders": sum(
                sum(p["predicted_orders"] for p in day["products"])
                for day in forecast_data
            ),
            "total_predicted_revenue": sum(
                sum(p["predicted_revenue"] for p in day["products"])
                for day in forecast_data
            ),
        },
    }


@app.get("/api/analytics/competitors")
async def competitors_analytics():
    """Аналитика конкурентов"""
    products = generate_mock_products()
    
    competitors = []
    for product in products[:5]:
        for i in range(1, 4):
            competitors.append({
                "product_name": f"{product['name']} (конкурент {i})",
                "price": product["price"] + random.randint(-500, 500),
                "rating": round(random.uniform(3.5, 5.0), 1),
                "reviews": random.randint(10, 500),
                "market_share": round(random.uniform(1, 15), 1),
            })
    
    return {
        "competitors": competitors,
        "price_comparison": [
            {
                "name": p["name"],
                "our_price": p["price"],
                "avg_competitor_price": p["price"] + random.randint(-300, 300),
                "position": random.choice(["cheaper", "more_expensive", "same"]),
            }
            for p in products[:5]
        ],
    }


FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"


@app.get("/api/analytics/returns")
async def returns_analytics():
    """Аналитика возвратов"""
    products = generate_mock_products()
    
    return_reasons = [
        {"reason": "Не подошёл размер", "count": random.randint(50, 150), "percent": 0},
        {"reason": "Не понравился товар", "count": random.randint(30, 100), "percent": 0},
        {"reason": "Брак / повреждение", "count": random.randint(20, 60), "percent": 0},
        {"reason": "Не соответствует описанию", "count": random.randint(15, 45), "percent": 0},
        {"reason": "Долгая доставка", "count": random.randint(10, 30), "percent": 0},
        {"reason": "Нашёл дешевле", "count": random.randint(8, 25), "percent": 0},
        {"reason": "Передумал покупать", "count": random.randint(12, 35), "percent": 0},
    ]
    
    total_returns = sum(r["count"] for r in return_reasons)
    for r in return_reasons:
        r["percent"] = round(r["count"] / total_returns * 100, 1) if total_returns > 0 else 0
    
    return_reasons.sort(key=lambda x: x["count"], reverse=True)
    
    total_orders = sum(p["orders"] for p in products)
    return_rate = round(total_returns / total_orders * 100, 1) if total_orders > 0 else 0
    
    returns_by_product = []
    for p in products[:5]:
        product_returns = random.randint(10, 80)
        returns_by_product.append({
            "nm_id": p["nm_id"],
            "name": p["name"],
            "orders": p["orders"],
            "returns": product_returns,
            "return_rate": round(product_returns / p["orders"] * 100, 1) if p["orders"] > 0 else 0,
            "return_cost": product_returns * p["price"],
        })
    
    returns_by_product.sort(key=lambda x: x["returns"], reverse=True)
    
    daily_returns = []
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        day_returns = random.randint(15, 50)
        daily_returns.append({
            "date": date,
            "returns": day_returns,
            "return_cost": day_returns * random.randint(500, 2000),
        })
    
    avg_return_cost = sum(r["return_cost"] for r in returns_by_product) / len(returns_by_product) if returns_by_product else 0
    
    return {
        "summary": {
            "total_returns": total_returns,
            "return_rate": return_rate,
            "total_orders": total_orders,
            "avg_return_cost": round(avg_return_cost),
            "total_return_cost": sum(r["return_cost"] for r in returns_by_product),
        },
        "reasons": return_reasons,
        "by_product": returns_by_product,
        "daily": daily_returns,
        "recommendations": [
            "Топ причина возвратов — размер. Добавьте подробную таблицу размеров на карточку товара",
            "Брак — вторая причина. Проверьте качество упаковки перед отправкой",
            "Снизьте возвраты за счёт качественных фото и подробного описания",
        ],
    }


@app.get("/app")
async def frontend():
    return FileResponse(FRONTEND_DIR / "index.html")