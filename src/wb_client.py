"""Wildberries API Client"""
import httpx
from typing import Optional, List
from datetime import datetime, timedelta


class WBApiClient:
    """Клиент для работы с Wildberries API"""
    
    BASE_URL = "https://suppliers-api.wildberries.ru"
    CONTENT_URL = "https://content-api.wildberries.ru"
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
    
    async def get_orders(self, date_from: Optional[str] = None, limit: int = 100) -> List[dict]:
        """Получение заказов"""
        if not date_from:
            date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00")
        
        url = f"{self.BASE_URL}/api/v5/supplier/orders"
        params = {"dateFrom": date_from, "limit": limit, "flag": 0}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params, timeout=15)
                if response.status_code == 200:
                    return response.json().get("orders", [])
                print(f"WB API error: {response.status_code}")
                return []
            except Exception as e:
                print(f"Error fetching WB orders: {e}")
                return []
    
    async def get_sales(self, date_from: Optional[str] = None, limit: int = 100) -> List[dict]:
        """Получение продаж"""
        if not date_from:
            date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00")
        
        url = f"{self.BASE_URL}/api/v5/supplier/sales"
        params = {"dateFrom": date_from, "limit": limit, "flag": 0}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params, timeout=15)
                if response.status_code == 200:
                    return response.json().get("sales", [])
                print(f"WB API error: {response.status_code}")
                return []
            except Exception as e:
                print(f"Error fetching WB sales: {e}")
                return []
    
    async def get_finance(self, date_from: Optional[str] = None, limit: int = 100) -> List[dict]:
        """Получение финансовых отчётов"""
        if not date_from:
            date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00")
        
        url = f"{self.BASE_URL}/api/v5/supplier/reportDetailByPeriod"
        params = {"dateFrom": date_from, "limit": limit, "flag": 0}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params, timeout=15)
                if response.status_code == 200:
                    return response.json().get("data", [])
                print(f"WB API error: {response.status_code}")
                return []
            except Exception as e:
                print(f"Error fetching WB finance: {e}")
                return []
    
    async def get_stocks(self, limit: int = 100) -> List[dict]:
        """Получение остатков"""
        url = f"{self.BASE_URL}/api/v5/supplier/stocks"
        params = {"limit": limit, "flag": 0}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params, timeout=15)
                if response.status_code == 200:
                    return response.json().get("stocks", [])
                print(f"WB API error: {response.status_code}")
                return []
            except Exception as e:
                print(f"Error fetching WB stocks: {e}")
                return []
    
    async def get_products(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """Получение списка товаров"""
        url = f"{self.CONTENT_URL}/content/v2/get/cards/list"
        params = {"limit": limit, "offset": offset}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params, timeout=15)
                if response.status_code == 200:
                    return response.json().get("cards", [])
                print(f"WB API error: {response.status_code}")
                return []
            except Exception as e:
                print(f"Error fetching WB products: {e}")
                return []
    
    async def get_cash_flow(self, date_from: Optional[str] = None) -> List[dict]:
        """Получение денежных потоков"""
        if not date_from:
            date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00")
        
        url = f"{self.BASE_URL}/api/v5/supplier/cash-flow"
        params = {"dateFrom": date_from}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params, timeout=15)
                if response.status_code == 200:
                    return response.json().get("cash_flows", [])
                print(f"WB API error: {response.status_code}")
                return []
            except Exception as e:
                print(f"Error fetching WB cash flow: {e}")
                return []