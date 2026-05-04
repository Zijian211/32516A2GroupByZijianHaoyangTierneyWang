from fastapi import FastAPI, status, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import os
import re
from bson import ObjectId # --- Added To Handle MongoDB's Native IDs ---
from bson.errors import InvalidId # --- To Catch Invalid ObjectId Formats ---

from passlib.context import CryptContext
from jose import JWTError, jwt

# --- Pydantic Model For CartItem ---
# --- 1. Product Model (Digital Goods: Phones, Watches, Laptops) ---
class Product(BaseModel):
    name: str
    price: float
    description: str
    image: str
    category: str

# --- 2. User Model (Handles Authentication With Strict Validation) ---
class User(BaseModel):
    username: str
    email: str
    password: str

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9]+$', v):
            raise ValueError("Username cannot contain any special characters")
        return v

    @field_validator('email')
    @classmethod
    def email_valid(cls, v: str) -> str:
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', v):
            raise ValueError("Invalid email format")
        return v

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9]+$', v):
            raise ValueError("Username cannot contain any special characters")
        return v

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class PasswordChange(BaseModel):
    old_password: str
    new_password: str
    confirm_new_password: str

# --- 3. Cart Item & Cart Model (Tied To A Specific User) ---
class CartItem(BaseModel):
    user_id: str # --- It Knows Who Owns The Cart Item ---
    product_id: str
    name: str
    price: float
    quantity: int
    image: str

class UserCart(BaseModel):
    user_id: str
    items: List[CartItem] = []

# --- 4. Order Model (Created When "Checkout" Is Clicked) ---
class Order(BaseModel):
    user_id: str
    items: List[CartItem]
    total_price: float
    status: str = "Completed" # --- Instantly Completed For This Order Without Transaction ---
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- Load The Secret URL From The .env File ---
load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

# --- CORS Middleware For React ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://32516-a1-zijian-hua.vercel.app"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Connect to Database when the app starts ---
@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(MONGODB_URL)
    app.database = app.mongodb_client.ecommerce_db
    print("Connected to the MongoDB database!")

# --- Disconnect when the app shuts down ---
@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

# ==========================================
# 🟩 CREATE (POST) - Green Block In Docs
# ==========================================

# --- User Signup With Validation ---
@app.post("/auth/signup", status_code=status.HTTP_201_CREATED, tags=["Create (POST)"])
async def signup(user: User):
    user_collection = app.database.users
    existing_user = await user_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    new_user = user.dict()
    new_user["password"] = pwd_context.hash(user.password) 
    await user_collection.insert_one(new_user)
    return {"message": f"User {user.username} created successfully!"}

# --- User Login With Validation ---
@app.post("/auth/login", tags=["Create (POST)"])
async def login(credentials: UserLogin):
    user_collection = app.database.users
    user = await user_collection.find_one({"username": credentials.username})
    
    if not user or not pwd_context.verify(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    token = jwt.encode(
        {"sub": str(user["_id"]), "exp": expire},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )
    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user_id": str(user["_id"]) 
    }

# --- Add To Cart Endpoint With Validation ---
@app.post("/cart", status_code=status.HTTP_201_CREATED, tags=["Create (POST)"])
async def add_to_cart(item: CartItem):
    try:
        official_product = await app.database.products.find_one({"_id": ObjectId(item.product_id)})
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Product ID format")
    
    if not official_product:
        raise HTTPException(status_code=404, detail="Product not found in store")

    cart_collection = app.database.cart
    existing_item = await cart_collection.find_one({"product_id": item.product_id, "user_id": item.user_id})
    
    if existing_item:
        new_quantity = existing_item["quantity"] + item.quantity
        await cart_collection.update_one(
            {"product_id": item.product_id, "user_id": item.user_id},
            {"$set": {"quantity": new_quantity}}
        )
        return {"message": "Cart quantity updated!"}
    
    new_cart_entry = item.dict()
    await cart_collection.insert_one(new_cart_entry)
    return {"message": "Successfully added to cart!"}

# --- Create Order Endpoint With Validation ---
@app.post("/orders", status_code=status.HTTP_201_CREATED, tags=["Create (POST)"])
async def create_new_order(user_id: str):
    cart_items = await app.database.cart.find({"user_id": user_id}).to_list(100)
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
        
    total_price = sum(item["price"] * item["quantity"] for item in cart_items)
    
    new_order = {
        "user_id": user_id,
        "items": cart_items,
        "total_price": total_price,
        "status": "Completed",
        "created_at": datetime.now(timezone.utc)
    }
    await app.database.orders.insert_one(new_order)
    await app.database.cart.delete_many({"user_id": user_id})
    return {"message": "Order created successfully!"}


# ==========================================
# 🟦 READ (GET) - Blue Block In Docs
# ==========================================

# --- Home Route To Test API Connection ---
@app.get("/", tags=["Read (GET)"])
def home():
    return {"message": "API Connection Ready!"}

# --- Get All Products (No Authentication Required) ---
@app.get("/products", tags=["Read (GET)"])
async def get_products():
    products = await app.database.products.find().to_list(100)
    for product in products: product["_id"] = str(product["_id"])
    return products

# --- Get All Users (For Admin Purposes, No Passwords Returned) ---
@app.get("/users", tags=["Read (GET)"])
async def get_users():
    users = await app.database.users.find().to_list(1000)
    for u in users: 
        u["_id"] = str(u["_id"])
        u.pop("password", None) # Security: Hide passwords from JSON return
    return users

# --- Get User's Cart Items ---
@app.get("/cart/{user_id}", tags=["Read (GET)"])
async def get_cart(user_id: str):
    items = await app.database.cart.find({"user_id": user_id}).to_list(100)
    for item in items: item["_id"] = str(item["_id"])
    return items

# --- Get User's Orders ---
@app.get("/orders/{user_id}", tags=["Read (GET)"])
async def get_user_orders(user_id: str):
    orders = await app.database.orders.find({"user_id": user_id}).to_list(100)
    for o in orders:
        o["_id"] = str(o["_id"])
        for item in o["items"]:
            if "_id" in item: item["_id"] = str(item["_id"])
    return orders


# ==========================================
# 🟨 UPDATE (PUT) - Yellow Block In Docs
# ==========================================

# --- Change Password Endpoint With Validation ---
@app.put("/users/{user_id}/password", tags=["Update (PUT)"])
async def change_password(user_id: str, data: PasswordChange):
    if data.new_password != data.confirm_new_password:
        raise HTTPException(status_code=400, detail="New passwords do not match")
        
    try:
        user_obj_id = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid User ID")

    db_user = await app.database.users.find_one({"_id": user_obj_id})
    if not db_user or db_user["password"] != data.old_password:
        raise HTTPException(status_code=401, detail="Incorrect old password")
        
    await app.database.users.update_one({"_id": user_obj_id}, {"$set": {"password": data.new_password}})
    return {"message": "Password updated successfully"}

# --- Update Cart Item Quantity With Validation ---
@app.put("/cart/{user_id}/{product_id}", tags=["Update (PUT)"])
async def update_cart_quantity(user_id: str, product_id: str, quantity: int = Query(gt=0)):
    result = await app.database.cart.update_one(
        {"product_id": product_id, "user_id": user_id},
        {"$set": {"quantity": quantity}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found in cart")
    return {"message": "Quantity updated successfully"}

# --- Update Order Item Quantity With Validation (Bonus) ---
@app.put("/orders/{user_id}/{order_id}", tags=["Update (PUT)"])
async def update_order_items(user_id: str, order_id: str, product_id: str, new_quantity: int = Query(gt=0)):
    """FIX: Now properly finds a specific product inside an order, updates its quantity, and recalculates total price."""
    try:
        order_obj_id = ObjectId(order_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Order ID")

    order = await app.database.orders.find_one({"_id": order_obj_id, "user_id": user_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    item_found = False
    updated_items = []
    for item in order["items"]:
        if item["product_id"] == product_id:
            item["quantity"] = new_quantity
            item_found = True
        updated_items.append(item)

    if not item_found:
        raise HTTPException(status_code=404, detail="Product not found in this order")

    new_total_price = sum(item["price"] * item["quantity"] for item in updated_items)

    await app.database.orders.update_one(
        {"_id": order_obj_id},
        {"$set": {"items": updated_items, "total_price": new_total_price}}
    )
    return {"message": "Order item quantity updated and total price recalculated"}


# ==========================================
# 🟥 DELETE (DELETE) - Red Block In Docs
# ==========================================

# --- Delete User Account With Validation (Also Deletes Cart & Orders) ---
@app.delete("/users/{user_id}", tags=["Delete (DELETE)"])
async def delete_account(user_id: str):
    try:
        user_obj_id = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid User ID")

    await app.database.users.delete_one({"_id": user_obj_id})
    await app.database.cart.delete_many({"user_id": user_id})
    await app.database.orders.delete_many({"user_id": user_id})
    return {"message": "Account permanently deleted"}

# --- Delete Item From Cart With Validation ---
@app.delete("/cart/{user_id}/{product_id}", tags=["Delete (DELETE)"])
async def delete_from_cart(user_id: str, product_id: str):
    result = await app.database.cart.delete_one({"product_id": product_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    return {"message": "Item removed from cart"}

# --- Delete Entire Order With Validation ---
@app.delete("/orders/{user_id}/{order_id}", tags=["Delete (DELETE)"])
async def delete_order(user_id: str, order_id: str):
    try:
        order_obj_id = ObjectId(order_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Order ID")

    result = await app.database.orders.delete_one({"_id": order_obj_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}