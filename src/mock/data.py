"""Мок-данные для Wildberries API"""
import random
from datetime import datetime, timedelta


def generate_mock_orders(count=100):
    """Генерация тестовых заказов"""
    products = [
        {"nm_id": 12345678, "article": "WB-001", "name": "Наушники беспроводные", "brand": "SoundMax"},
        {"nm_id": 23456789, "article": "WB-002", "name": "Чехол для iPhone 15", "brand": "CasePro"},
        {"nm_id": 34567890, "article": "WB-003", "name": "Кабель USB-C 2м", "brand": "CableTech"},
        {"nm_id": 45678901, "article": "WB-004", "name": "Повербанк 10000mAh", "brand": "PowerUp"},
        {"nm_id": 56789012, "article": "WB-005", "name": "Стекло защитное", "brand": "ScreenGuard"},
        {"nm_id": 67890123, "article": "WB-006", "name": "Наушники проводные", "brand": "SoundMax"},
        {"nm_id": 78901234, "article": "WB-007", "name": "Держатель для телефона", "brand": "AutoMount"},
        {"nm_id": 89012345, "article": "WB-008", "name": "Зарядка быстрая 65W", "brand": "PowerUp"},
        {"nm_id": 90123456, "article": "WB-009", "name": "Коврик для мыши", "brand": "DeskPro"},
        {"nm_id": 11223344, "article": "WB-010", "name": "Клавиатура механическая", "brand": "KeyMaster"},
    ]
    
    orders = []
    for i in range(count):
        product = random.choice(products)
        days_ago = random.randint(0, 30)
        order_date = datetime.now() - timedelta(days=days_ago)
        
        price = random.randint(500, 5000)
        discount = random.choice([0, 0, 0, 10, 15, 20, 25, 30])
        final_price = int(price * (1 - discount / 100))
        
        orders.append({
            "srid": f"test-{i:06d}",
            "date": order_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "nmId": product["nm_id"],
            "supplierArticle": product["article"],
            "barcode": f"20{i:08d}",
            "category": "Электроника",
            "subject": "Аксессуары",
            "brand": product["brand"],
            "techSize": random.choice(["XS", "S", "M", "L", "XL", "universal"]),
            "totalPrice": price,
            "discountPercent": discount,
            "finishedPrice": final_price,
            "priceWithDisc": final_price,
            "warehouseName": random.choice(["Москва", "Казань", "Краснодар", "Екатеринбург"]),
            "regionName": random.choice(["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань"]),
            "isCancel": random.random() < 0.05,
            "cancelDate": None,
            "sticker": "",
            "gNumber": f"test-g{i:06d}",
        })
    
    return orders


def generate_mock_sales(count=80):
    """Генерация тестовых продаж"""
    products = [
        {"nm_id": 12345678, "article": "WB-001", "name": "Наушники беспроводные", "price": 2500},
        {"nm_id": 23456789, "article": "WB-002", "name": "Чехол для iPhone 15", "price": 890},
        {"nm_id": 34567890, "article": "WB-003", "name": "Кабель USB-C 2м", "price": 450},
        {"nm_id": 45678901, "article": "WB-004", "name": "Повербанк 10000mAh", "price": 1990},
        {"nm_id": 56789012, "article": "WB-005", "name": "Стекло защитное", "price": 350},
        {"nm_id": 67890123, "article": "WB-006", "name": "Наушники проводные", "price": 790},
        {"nm_id": 78901234, "article": "WB-007", "name": "Держатель для телефона", "price": 650},
        {"nm_id": 89012345, "article": "WB-008", "name": "Зарядка быстрая 65W", "price": 1490},
    ]
    
    sales = []
    for i in range(count):
        product = random.choice(products)
        days_ago = random.randint(0, 30)
        sale_date = datetime.now() - timedelta(days=days_ago)
        
        for_price = int(product["price"] * 0.9)
        retail_price = product["price"]
        seller_price = int(retail_price * 0.85)
        
        wb_fee = int(retail_price * 0.15)
        logistics = random.randint(30, 80)
        storage = random.randint(5, 20)
        
        sales.append({
            "rr_dt": sale_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "nm_id": product["nm_id"],
            "supplier_article": product["article"],
            "barcode": f"20{i:08d}",
            "category": "Электроника",
            "subject": "Аксессуары",
            "brand": "TestBrand",
            "techSize": "universal",
            "for_pay": for_price,
            "finished_price": retail_price,
            "price_with_disc": seller_price,
            "sale_total": seller_price,
            "spp": 0,
            "payment_sale_amount": for_price,
            "is_return": 0,
        })
    
    return sales


def generate_mock_finance(days=30):
    """Генерация тестовых финансовых данных"""
    finance = []
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        
        sales_amount = random.randint(50000, 200000)
        sales_count = random.randint(10, 50)
        
        for sale in range(sales_count):
            sale_amount = random.randint(300, 3000)
            fee = int(sale_amount * 0.15)
            logistics = random.randint(30, 80)
            storage = random.randint(2, 15)
            
            finance.append({
                "date": date,
                "operation_type": "Продажа",
                "sku": f"WB-{random.randint(100, 999)}",
                "quantity": 1,
                "retail_price": sale_amount,
                "retail_amount": sale_amount,
                "sale_amount": sale_amount,
                "payment_amount": sale_amount - fee,
                "service_fee": fee,
                "penalty": 0,
                "additional_payment": 0,
            })
        
        storage_cost = random.randint(1000, 5000)
        finance.append({
            "date": date,
            "operation_type": "Хранение",
            "sku": "ALL",
            "quantity": 1,
            "retail_price": storage_cost,
            "retail_amount": storage_cost,
            "sale_amount": 0,
            "payment_amount": -storage_cost,
            "service_fee": 0,
            "penalty": 0,
            "additional_payment": 0,
        })
        
        if random.random() < 0.1:
            penalty = random.randint(500, 5000)
            finance.append({
                "date": date,
                "operation_type": "Штраф",
                "sku": f"WB-{random.randint(100, 999)}",
                "quantity": 1,
                "retail_price": penalty,
                "retail_amount": penalty,
                "sale_amount": 0,
                "payment_amount": -penalty,
                "service_fee": 0,
                "penalty": penalty,
                "additional_payment": 0,
            })
    
    return finance


def generate_mock_stocks():
    """Генерация тестовых остатков"""
    products = [
        {"nm_id": 12345678, "article": "WB-001", "name": "Наушники беспроводные", "price": 2500},
        {"nm_id": 23456789, "article": "WB-002", "name": "Чехол для iPhone 15", "price": 890},
        {"nm_id": 34567890, "article": "WB-003", "name": "Кабель USB-C 2м", "price": 450},
        {"nm_id": 45678901, "article": "WB-004", "name": "Повербанк 10000mAh", "price": 1990},
        {"nm_id": 56789012, "article": "WB-005", "name": "Стекло защитное", "price": 350},
    ]
    
    stocks = []
    warehouses = ["Москва", "Казань", "Краснодар"]
    
    for product in products:
        for warehouse in warehouses:
            stocks.append({
                "barcode": f"20{product['nm_id']}",
                "nm_id": product["nm_id"],
                "supplier_article": product["article"],
                "category": "Электроника",
                "subject": "Аксессуары",
                "brand": "TestBrand",
                "techSize": "universal",
                "warehouse_name": warehouse,
                "lastFreeOverturnDays": random.randint(1, 30),
                "daysWithoutSales": random.randint(0, 60),
                "stock": random.randint(5, 100),
                "stockMP": 0,
                "inWayFromClient": 0,
                "inWayToClient": random.randint(0, 20),
                "inTransit": 0,
                "price": product["price"],
            })
    
    return stocks


def generate_mock_products():
    """Генерация тестовых товаров"""
    return [
        {"nm_id": 12345678, "article": "WB-001", "name": "Наушники беспроводные TWS", "brand": "SoundMax", "price": 2500, "rating": 4.5, "reviews": 234, "orders": 1567, "category": "Электроника"},
        {"nm_id": 23456789, "article": "WB-002", "name": "Чехол для iPhone 15 Pro", "brand": "CasePro", "price": 890, "rating": 4.2, "reviews": 567, "orders": 3421, "category": "Электроника"},
        {"nm_id": 34567890, "article": "WB-003", "name": "Кабель USB-C Type-C 2м", "brand": "CableTech", "price": 450, "rating": 4.7, "reviews": 892, "orders": 5678, "category": "Электроника"},
        {"nm_id": 45678901, "article": "WB-004", "name": "Повербанк 10000 mAh", "brand": "PowerUp", "price": 1990, "rating": 4.3, "reviews": 123, "orders": 890, "category": "Электроника"},
        {"nm_id": 56789012, "article": "WB-005", "name": "Стекло защитное 9H", "brand": "ScreenGuard", "price": 350, "rating": 4.1, "reviews": 456, "orders": 4567, "category": "Электроника"},
        {"nm_id": 67890123, "article": "WB-006", "name": "Наушники проводные 3.5мм", "brand": "SoundMax", "price": 790, "rating": 4.4, "reviews": 678, "orders": 2345, "category": "Электроника"},
        {"nm_id": 78901234, "article": "WB-007", "name": "Держатель для авто", "brand": "AutoMount", "price": 650, "rating": 4.6, "reviews": 345, "orders": 1890, "category": "Электроника"},
        {"nm_id": 89012345, "article": "WB-008", "name": "Зарядное устройство 65W", "brand": "PowerUp", "price": 1490, "rating": 4.8, "reviews": 234, "orders": 1234, "category": "Электроника"},
        {"nm_id": 90123456, "article": "WB-009", "name": "Коврик для мыши XL", "brand": "DeskPro", "price": 590, "rating": 4.0, "reviews": 123, "orders": 567, "category": "Электроника"},
        {"nm_id": 11223344, "article": "WB-010", "name": "Клавиатура RGB механическая", "brand": "KeyMaster", "price": 3490, "rating": 4.7, "reviews": 89, "orders": 234, "category": "Электроника"},
    ]