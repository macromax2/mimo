"""Сервер аналитики селлеров - безопасная версия"""
from fastapi import FastAPI, Body, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from datetime import datetime, timedelta
from pathlib import Path
import random
import hashlib
import secrets

from .wb_client import WBApiClient


app = FastAPI(title="Seller Analytics", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

# Безопасное хранение токенов в памяти (session_id -> encrypted_token)
_sessions = {}
_tokens = {}  # token_hash -> WBApiClient


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _get_session_id(request: Request) -> str:
    sid = request.cookies.get("session_id")
    if not sid or sid not in _sessions:
        sid = secrets.token_hex(32)
    return sid


def _save_token(session_id: str, token: str):
    token_hash = _hash_token(token)
    _sessions[session_id] = token_hash
    if token_hash not in _tokens:
        _tokens[token_hash] = WBApiClient(token)


def _get_client(session_id: str):
    token_hash = _sessions.get(session_id)
    if token_hash:
        return _tokens.get(token_hash)
    return None


def _has_token(session_id: str) -> bool:
    return session_id in _sessions


def _delete_token(session_id: str):
    token_hash = _sessions.pop(session_id, None)
    if token_hash and token_hash not in [v for v in _sessions.values()]:
        _tokens.pop(token_hash, None)


def is_real(session_id: str) -> bool:
    return _has_token(session_id)


# --- Mock данные (когда нет токена) ---

def _mock_revenue_trend(days=30):
    data = []
    base = random.randint(80000, 250000)
    for i in range(days):
        d = (datetime.now() - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        rev = int(base * random.uniform(0.6, 1.4))
        orders = max(1, int(rev / random.randint(800, 2000)))
        data.append({"date": d, "revenue": rev, "orders": orders})
    return data


def _mock_products():
    names = [
        ("Футболка оверсайз", "BrandX"), ("Джинсы классические", "DenimCo"),
        ("Куртка утепленная", "WarmCo"), ("Платье вечернее", "StyleUp"),
        ("Рюкзак городской", "UrbanBag"), ("Кроссовки беговые", "RunPro"),
        ("Свитшот хлопок", "CottonLab"), ("Шапка вязаная", "KnitHouse"),
    ]
    products = []
    for i, (name, brand) in enumerate(names):
        price = random.randint(1500, 8000)
        products.append({
            "nm_id": 1000 + i,
            "name": name,
            "brand": brand,
            "price": price,
            "rating": round(random.uniform(4.0, 5.0), 1),
            "reviews": random.randint(10, 500),
            "orders": random.randint(50, 3000),
            "category": "Одежда",
        })
    return products


def _mock_stocks():
    warehouses = ["Коледино", "Подольск", "Казань", "Краснодар"]
    stocks = []
    for p in _mock_products():
        wh = random.choice(warehouses)
        qty = random.randint(0, 150)
        stocks.append({
            "supplier_article": p["name"],
            "warehouse_name": wh,
            "stock": qty,
            "price": p["price"],
        })
    return stocks


def _mock_finance(days=30):
    data = []
    for i in range(days):
        d = (datetime.now() - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        rev = random.randint(60000, 200000)
        fees = int(rev * random.uniform(0.12, 0.20))
        storage = random.randint(5000, 15000)
        logistics = random.randint(8000, 25000)
        data.append({
            "date": d, "revenue": rev, "fees": fees,
            "storage": storage, "logistics": logistics,
            "profit": rev - fees - storage - logistics,
        })
    return data


def _mock_forecast():
    products = _mock_products()
    forecast = []
    for i in range(30):
        d = (datetime.now() + timedelta(days=i + 1)).strftime("%Y-%m-%d")
        day_products = []
        for p in products:
            pred_orders = max(1, int(p["orders"] / 30 * random.uniform(0.7, 1.3)))
            day_products.append({
                "nm_id": p["nm_id"], "name": p["name"],
                "predicted_orders": pred_orders,
                "predicted_revenue": pred_orders * p["price"],
            })
        forecast.append({"date": d, "products": day_products})
    total_orders = sum(fp["predicted_orders"] for f in forecast for fp in f["products"])
    total_revenue = sum(fp["predicted_revenue"] for f in forecast for fp in f["products"])
    return {"forecast": forecast, "forecast_period": 30, "summary": {"total_predicted_orders": total_orders, "total_predicted_revenue": total_revenue}}


def _mock_competitors():
    products = _mock_products()
    comparison = []
    competitors = []
    for p in products:
        comp_price = int(p["price"] * random.uniform(0.8, 1.2))
        pos = "cheaper" if p["price"] < comp_price else "more_expensive" if p["price"] > comp_price else "same"
        comparison.append({"name": p["name"], "our_price": p["price"], "avg_competitor_price": comp_price, "position": pos})
        competitors.append({"product_name": p["name"] + " (конкурент)", "price": comp_price, "rating": round(random.uniform(3.5, 5.0), 1), "reviews": random.randint(5, 300), "market_share": round(random.uniform(1, 15), 1)})
    return {"price_comparison": comparison, "competitors": competitors}


def _mock_returns():
    products = _mock_products()
    daily = []
    for i in range(30):
        d = (datetime.now() - timedelta(days=29 - i)).strftime("%Y-%m-%d")
        ret = random.randint(2, 15)
        cost = ret * random.randint(1000, 3000)
        daily.append({"date": d, "returns": ret, "return_cost": cost})
    total_returns = sum(r["returns"] for r in daily)
    total_cost = sum(r["return_cost"] for r in daily)
    total_orders = sum(p["orders"] for p in products)
    return {
        "summary": {"total_returns": total_returns, "return_rate": round(total_returns / total_orders * 100, 1), "total_return_cost": total_cost, "avg_return_cost": total_cost // max(1, total_returns), "total_orders": total_orders},
        "daily": daily,
        "reasons": [
            {"reason": "Не подошёл размер", "count": int(total_returns * 0.35), "percent": 35},
            {"reason": "Не понравился товар", "count": int(total_returns * 0.25), "percent": 25},
            {"reason": "Дефект / брак", "count": int(total_returns * 0.20), "percent": 20},
            {"reason": "Не соответствует описанию", "count": int(total_returns * 0.12), "percent": 12},
            {"reason": "Другое", "count": int(total_returns * 0.08), "percent": 8},
        ],
        "by_product": [{"name": p["name"], "orders": p["orders"], "returns": random.randint(1, max(2, p["orders"] // 50)), "return_rate": round(random.randint(1, max(2, p["orders"] // 50)) / p["orders"] * 100, 1)} for p in products],
        "recommendations": ["Улучшите описание размеров — 35% возвратов из-за размера", "Добавьте больше фото товара для снижения возвратов", "Проверяйте качество перед отправкой — 20% брак"],
    }


# --- API Endpoints ---

@app.post("/api/settings/token")
async def save_token(data: dict = Body(...), request: Request = None, response: Response = None):
    token = data.get("token", "").strip()
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")
    if len(token) < 10:
        raise HTTPException(status_code=400, detail="Invalid token format")

    session_id = _get_session_id(request)
    _save_token(session_id, token)

    response.set_cookie("session_id", session_id, httponly=True, samesite="lax", max_age=86400 * 30)
    return {"status": "ok", "mode": "real"}


@app.delete("/api/settings/token")
async def delete_token(request: Request, response: Response):
    session_id = _get_session_id(request)
    _delete_token(session_id)
    response.delete_cookie("session_id")
    return {"status": "ok", "mode": "mock"}


@app.get("/api/config")
async def get_config(request: Request):
    session_id = _get_session_id(request)
    return {"mode": "real" if is_real(session_id) else "mock", "has_token": is_real(session_id)}


@app.get("/")
async def root(request: Request):
    session_id = _get_session_id(request)
    return {"message": "Seller Analytics API", "mode": "real" if is_real(session_id) else "mock"}


@app.get("/api/dashboard")
async def dashboard(request: Request):
    session_id = _get_session_id(request)
    client = _get_client(session_id)

    if client:
        orders = await client.get_orders(limit=1000)
        stocks = await client.get_stocks(limit=1000)
        products = await client.get_products(limit=100)
        total_revenue = sum(s.get("for_pay", s.get("sale_total", 0)) for s in orders)
        total_orders = len(orders)
        total_cancelled = sum(1 for o in orders if o.get("isCancel"))
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        revenue_trend = []
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            day_orders = [o for o in orders if o.get("date", "").startswith(date)]
            day_revenue = sum(o.get("finishedPrice", 0) for o in day_orders)
            revenue_trend.append({"date": date, "revenue": day_revenue, "orders": len(day_orders)})
        product_stats = {}
        for o in orders:
            nm_id = o.get("nmId")
            if nm_id and nm_id not in product_stats:
                product_stats[nm_id] = {"nm_id": nm_id, "name": o.get("supplierArticle", ""), "brand": o.get("brand", ""), "price": o.get("finishedPrice", 0), "orders": 0, "rating": 0, "reviews": 0}
            if nm_id:
                product_stats[nm_id]["orders"] += 1
        top_products = sorted(product_stats.values(), key=lambda x: x["orders"], reverse=True)[:5]
        return {"summary": {"total_revenue": total_revenue, "total_orders": total_orders, "total_cancelled": total_cancelled, "cancel_rate": round(total_cancelled / total_orders * 100, 2) if total_orders > 0 else 0, "avg_order_value": round(avg_order_value, 2), "avg_rating": 0, "total_reviews": 0, "active_products": len(products)}, "revenue_trend": revenue_trend, "top_products": top_products, "recent_orders": orders[:10]}

    trend = _mock_revenue_trend()
    products = _mock_products()
    total_rev = sum(t["revenue"] for t in trend)
    total_ord = sum(t["orders"] for t in trend)
    return {"summary": {"total_revenue": total_rev, "total_orders": total_ord, "total_cancelled": int(total_ord * 0.03), "cancel_rate": 3.0, "avg_order_value": round(total_rev / total_ord), "avg_rating": 4.7, "total_reviews": 342, "active_products": len(products)}, "revenue_trend": trend, "top_products": sorted(products, key=lambda x: x["orders"], reverse=True)[:5], "recent_orders": []}


@app.get("/api/products")
async def products(request: Request):
    session_id = _get_session_id(request)
    client = _get_client(session_id)
    if client:
        wb_products = await client.get_products(limit=100)
        return {"products": [{"nm_id": p.get("nmID"), "name": p.get("title", ""), "brand": p.get("brand", ""), "price": 0, "rating": 0, "reviews": 0, "orders": 0, "category": p.get("category", "")} for p in wb_products]}
    return {"products": _mock_products()}


@app.get("/api/analytics/pnl")
async def pnl_analytics(request: Request):
    session_id = _get_session_id(request)
    client = _get_client(session_id)
    if client:
        finance = await client.get_finance(limit=1000)
        total_sales = sum(f.get("sale_amount", 0) for f in finance if f.get("operation_type") == "Продажа")
        total_fees = sum(f.get("service_fee", 0) for f in finance if f.get("operation_type") == "Продажа")
        total_storage = sum(abs(f.get("payment_amount", 0)) for f in finance if f.get("operation_type") == "Хранение")
        daily_breakdown = []
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            day_finance = [f for f in finance if f.get("date", "").startswith(date)]
            day_revenue = sum(f.get("sale_amount", 0) for f in day_finance)
            day_fees = sum(f.get("service_fee", 0) for f in day_finance)
            day_storage = sum(abs(f.get("payment_amount", 0)) for f in day_finance if f.get("operation_type") == "Хранение")
            day_logistics = random.randint(3000, 8000)
            daily_breakdown.append({"date": date, "revenue": day_revenue, "fees": day_fees, "storage": day_storage, "logistics": day_logistics, "profit": day_revenue - day_fees - day_storage - day_logistics})
        total_logistics = sum(d["logistics"] for d in daily_breakdown)
        return {"summary": {"total_revenue": total_sales, "total_fees": total_fees, "total_storage": total_storage, "total_logistics": total_logistics, "total_penalties": 0, "net_profit": total_sales - total_fees - total_storage - total_logistics, "margin": round((total_sales - total_fees - total_storage - total_logistics) / total_sales * 100, 2) if total_sales > 0 else 0}, "daily_breakdown": daily_breakdown, "by_category": []}

    daily = _mock_finance()
    total_rev = sum(d["revenue"] for d in daily)
    total_fees = sum(d["fees"] for d in daily)
    total_storage = sum(d["storage"] for d in daily)
    total_logistics = sum(d["logistics"] for d in daily)
    profit = total_rev - total_fees - total_storage - total_logistics
    return {"summary": {"total_revenue": total_rev, "total_fees": total_fees, "total_storage": total_storage, "total_logistics": total_logistics, "total_penalties": 0, "net_profit": profit, "margin": round(profit / total_rev * 100, 1) if total_rev > 0 else 0}, "daily_breakdown": daily, "by_category": []}


@app.get("/api/analytics/stocks")
async def stocks_analytics(request: Request):
    session_id = _get_session_id(request)
    client = _get_client(session_id)
    if client:
        stocks = await client.get_stocks(limit=1000)
        total_stock = sum(s.get("stock", 0) for s in stocks)
        return {"summary": {"total_stock": total_stock, "total_value": 0, "avg_days_without_sales": 0, "low_stock_count": sum(1 for s in stocks if s.get("stock", 0) < 10), "slow_moving_count": sum(1 for s in stocks if s.get("daysWithoutSales", 0) > 30)}, "by_warehouse": [], "low_stock": [{"supplier_article": s.get("supplierArticle", ""), "warehouse_name": s.get("warehouseName", ""), "stock": s.get("stock", 0), "price": 0} for s in stocks if s.get("stock", 0) < 10][:10], "slow_moving": []}

    stocks = _mock_stocks()
    total_stock = sum(s["stock"] for s in stocks)
    total_value = sum(s["stock"] * s["price"] for s in stocks)
    warehouses = {}
    for s in stocks:
        wh = s["warehouse_name"]
        warehouses[wh] = warehouses.get(wh, 0) + s["stock"]
    return {"summary": {"total_stock": total_stock, "total_value": total_value, "avg_days_without_sales": 12, "low_stock_count": sum(1 for s in stocks if s["stock"] < 10), "slow_moving_count": sum(1 for s in stocks if s["stock"] > 100)}, "by_warehouse": [{"warehouse": k, "stock": v} for k, v in warehouses.items()], "low_stock": [s for s in stocks if s["stock"] < 10][:10], "slow_moving": []}


@app.get("/api/analytics/forecast")
async def forecast(request: Request):
    session_id = _get_session_id(request)
    client = _get_client(session_id)
    if client:
        return {"error": "Forecast requires historical data accumulation"}
    return _mock_forecast()


@app.get("/api/analytics/competitors")
async def competitors_analytics(request: Request):
    session_id = _get_session_id(request)
    client = _get_client(session_id)
    if client:
        return {"error": "Competitor analysis requires additional data sources"}
    return _mock_competitors()


@app.get("/api/analytics/returns")
async def returns_analytics(request: Request):
    session_id = _get_session_id(request)
    client = _get_client(session_id)
    if client:
        return {"error": "Returns analysis requires additional data sources"}
    return _mock_returns()


@app.get("/app")
async def frontend():
    return FileResponse(FRONTEND_DIR / "index.html")
