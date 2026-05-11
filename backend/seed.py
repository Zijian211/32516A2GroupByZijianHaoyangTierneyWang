import os
import asyncio
from pathlib import Path
from passlib.context import CryptContext
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# --- This Finds The Directory Where Seed.py Is Actually Sitting ---
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"

# --- Load The .env Using The Absolute Path ---
load_dotenv(dotenv_path=env_path)

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "final_ecommerce_db")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# --- Initialise Admin Password Context For Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_database():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_DB_NAME]
    
    if ADMIN_USERNAME and ADMIN_EMAIL and ADMIN_PASSWORD:
        await db.users.update_one(
            {"username": ADMIN_USERNAME},
            {
                "$set": {
                    "username": ADMIN_USERNAME,
                    "email": ADMIN_EMAIL,
                    "password": pwd_context.hash(ADMIN_PASSWORD),
                    "role": "admin"
                }
            },
            upsert=True
        )
        print(f"Admin user '{ADMIN_USERNAME}' seeded successfully.")
    else:
        print("Admin user seed skipped. ADMIN_USERNAME, ADMIN_EMAIL, or ADMIN_PASSWORD is not set.")

    await db.products.delete_many({}) # --- Clear Old Data ---
    
    products = [
        {"name": "MacBook Pro 14", "price": 1999.00, "category": "Laptops", "image": "https://m.media-amazon.com/images/I/71hu5w9zCXL._AC_UY218_.jpg", "description": "Apple M3 Pro chip, 18GB Unified Memory, 512GB SSD."},
        {"name": "Dell XPS 13", "price": 1299.00, "category": "Laptops", "image": "https://m.media-amazon.com/images/I/61a3VUNrd4L._AC_UY218_.jpg", "description": "Intel Core i7, 16GB RAM, 13.4-inch display."},
        {"name": "ASUS ROG Zephyrus", "price": 1599.99, "category": "Laptops", "image": "https://m.media-amazon.com/images/I/71kq-Q4RvgL._AC_UY218_.jpg", "description": "Gaming Laptop, RTX 4070, 165Hz Display."},
        {"name": "HP Spectre x360", "price": 1399.00, "category": "Laptops", "image": "https://m.media-amazon.com/images/I/61wdZ89-JWL._AC_UY218_.jpg", "description": "2-in-1 Touchscreen Laptop, Intel EVO."},
        {"name": "Lenovo ThinkPad X1", "price": 1450.00, "category": "Laptops", "image": "https://m.media-amazon.com/images/I/71HEN-rzYfL._AC_UY218_.jpg", "description": "Business standard, Carbon Fiber build."},
        {"name": "iPhone 15 Pro", "price": 999.00, "category": "Phones", "image": "https://m.media-amazon.com/images/I/51PtFHUPjBL._AC_UY218_.jpg", "description": "Titanium design, A17 Pro chip."},
        {"name": "Samsung Galaxy S24 Ultra", "price": 1299.00, "category": "Phones", "image": "https://m.media-amazon.com/images/I/41emO6FOHvL._AC_UY218_.jpg", "description": "AI-powered, 200MP camera, built-in S Pen."},
        {"name": "Google Pixel 8 Pro", "price": 899.00, "category": "Phones", "image": "https://m.media-amazon.com/images/I/612MWk6S3kL._AC_UY218_.jpg", "description": "Advanced camera system, Google AI."},
        {"name": "OnePlus 12", "price": 799.00, "category": "Phones", "image": "https://m.media-amazon.com/images/I/51zoLE5g5XL._AC_UY218_.jpg", "description": "Snapdragon 8 Gen 3, 50MP camera."},
        {"name": "Sony Xperia 1 V", "price": 1198.00, "category": "Phones", "image": "https://m.media-amazon.com/images/I/61Wd-aDMBEL._AC_UY218_.jpg", "description": "4K HDR OLED display, Pro camera controls."},
        {"name": "Apple Watch Ultra 2", "price": 799.00, "category": "Watches", "image": "https://m.media-amazon.com/images/I/6165pya85SL._AC_UY218_.jpg", "description": "Rugged Titanium, GPS + Cellular."},
        {"name": "Samsung Galaxy Watch 6", "price": 299.00, "category": "Watches", "image": "https://m.media-amazon.com/images/I/61NJKdXqx5L._AC_UY218_.jpg", "description": "Health tracking, Sleep coaching."},
        {"name": "Garmin Fenix 7 Pro", "price": 699.99, "category": "Watches", "image": "https://m.media-amazon.com/images/I/71xr9LGXt+L._AC_UY218_.jpg", "description": "Multisport GPS watch, Solar charging."},
        {"name": "Google Pixel Watch 2", "price": 349.00, "category": "Watches", "image": "https://m.media-amazon.com/images/I/71nEDjUiHGL._AC_UY218_.jpg", "description": "Fitbit health tracking, AI heart rate sensor."},
        {"name": "Tag Heuer Connected", "price": 1800.00, "category": "Watches", "image": "https://m.media-amazon.com/images/I/61u5XSi-38L._AC_UY218_.jpg", "description": "Luxury smart watch, Stainless Steel case."},
        {"name": "iPad Pro 12.9", "price": 1099.00, "category": "Tablets", "image": "https://m.media-amazon.com/images/I/61aPY8odPSL._AC_UY218_.jpg", "description": "Liquid Retina XDR, M2 chip."},
        {"name": "Samsung Galaxy Tab S9", "price": 799.00, "category": "Tablets", "image": "https://m.media-amazon.com/images/I/61lOqBG9HiL._AC_UY218_.jpg", "description": "Dynamic AMOLED 2X, Water resistant."},
        {"name": "Microsoft Surface Pro 9", "price": 999.99, "category": "Tablets", "image": "https://m.media-amazon.com/images/I/516odOsANqL._AC_UY218_.jpg", "description": "Laptop versatility, Intel Evo 12th Gen."},
        {"name": "Amazon Fire Max 11", "price": 229.00, "category": "Tablets", "image": "https://m.media-amazon.com/images/I/61d0nRJ7UJL._AC_UY218_.jpg", "description": "Octa-core processor, 14-hour battery."},
        {"name": "Lenovo Tab P11 Pro", "price": 429.00, "category": "Tablets", "image": "https://m.media-amazon.com/images/I/71bDdiCbWmL._AC_UY218_.jpg", "description": "11.2-inch OLED display, Cinematic audio."}
    ]
    
    await db.products.insert_many(products)
    print(f"Successfully seeded {len(products)} products.")

if __name__ == "__main__":
    asyncio.run(seed_database())