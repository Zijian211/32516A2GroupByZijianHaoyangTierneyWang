from fastapi import FastAPI, status, HTTPException, Query, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import os
import re
from bson import ObjectId
from bson.errors import InvalidId
from passlib.context import CryptContext
from jose import JWTError, jwt

# --- Pydantic Models ---
class Product(BaseModel):
    name: str
    price: float
    description: str
    image: str
    category: str

class User(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"

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

class CartItem(BaseModel):
    user_id: str
    product_id: str
    name: str
    price: float
    quantity: int
    image: str

class UserCart(BaseModel):
    user_id: str
    items: List[CartItem] = []

class Order(BaseModel):
    user_id: str
    items: List[CartItem]
    total_price: float
    status: str = "Completed"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- Load Env ---
load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "final_ecommerce_db")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = 60 * 24

# --- Auth Tools ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()

# --- JWT Helper Functions ---
def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(user_id: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": user_id, "role": role, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# --- Dependency: Any logged-in user ---
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalid or expired")

    try:
        user_obj_id = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    db_user = await app.database.users.find_one({"_id": user_obj_id})
    if db_user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")

    return {
        "user_id": str(db_user["_id"]),
        "username": db_user["username"],
        "role": db_user.get("role", "user")
    }

# --- Dependency: Admin only ---
async def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://32516-a1-zijian-hua.vercel.app"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DB Lifecycle ---
@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(MONGODB_URL)
    app.database = app.mongodb_client[MONGODB_DB_NAME]
    print(f"Connected to MongoDB database: {MONGODB_DB_NAME}")

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

# ==========================================
# CREATE (POST)
# ==========================================

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED, tags=["Create (POST)"])
async def signup(user: User):
    user_collection = app.database.users
    existing_user = await user_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    new_user = user.dict()
    new_user["password"] = hash_password(user.password)
    new_user["role"] = "user"  
    await user_collection.insert_one(new_user)
    return {"message": f"User {user.username} created successfully!"}

@app.post("/auth/login", tags=["Create (POST)"])
async def login(credentials: UserLogin):
    user_collection = app.database.users
    user = await user_collection.find_one({"username": credentials.username})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token(str(user["_id"]), user.get("role", "user"))
    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user_id": str(user["_id"]),
        "username": user["username"],
        "role": user.get("role", "user")
    }

@app.post("/cart", status_code=status.HTTP_201_CREATED, tags=["Create (POST)"])
async def add_to_cart(item: CartItem, current_user: dict = Depends(get_current_user)):
    if current_user["user_id"] != item.user_id and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
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
    await cart_collection.insert_one(item.dict())
    return {"message": "Successfully added to cart!"}

@app.post("/orders", status_code=status.HTTP_201_CREATED, tags=["Create (POST)"])
async def create_new_order(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["user_id"] != user_id and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
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
# READ (GET)
# ==========================================

@app.get("/", tags=["Read (GET)"])
def home():
    return {"message": "API Connection Ready!"}

@app.get("/products", tags=["Read (GET)"])
async def get_products():
    products = await app.database.products.find().to_list(100)
    for product in products:
        product["_id"] = str(product["_id"])
    return products

@app.get("/users", tags=["Read (GET)"])
async def get_users(current_user: dict = Depends(require_admin)):
    users = await app.database.users.find().to_list(1000)
    for u in users:
        u["_id"] = str(u["_id"])
        u.pop("password", None)
    return users

@app.get("/cart/{user_id}", tags=["Read (GET)"])
async def get_cart(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["user_id"] != user_id and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    items = await app.database.cart.find({"user_id": user_id}).to_list(100)
    for item in items:
        item["_id"] = str(item["_id"])
    return items

@app.get("/orders/{user_id}", tags=["Read (GET)"])
async def get_user_orders(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["user_id"] != user_id and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    orders = await app.database.orders.find({"user_id": user_id}).to_list(100)
    for o in orders:
        o["_id"] = str(o["_id"])
        for item in o["items"]:
            if "_id" in item:
                item["_id"] = str(item["_id"])
    return orders

# ==========================================
# UPDATE (PUT)
# ==========================================

@app.put("/users/{user_id}/password", tags=["Update (PUT)"])
async def change_password(user_id: str, data: PasswordChange, current_user: dict = Depends(get_current_user)):
    if current_user["user_id"] != user_id and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    if data.new_password != data.confirm_new_password:
        raise HTTPException(status_code=400, detail="New passwords do not match")
    try:
        user_obj_id = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid User ID")
    db_user = await app.database.users.find_one({"_id": user_obj_id})
    if not db_user or not verify_password(data.old_password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect old password")
    hashed_new = hash_password(data.new_password)
    await app.database.users.update_one({"_id": user_obj_id}, {"$set": {"password": hashed_new}})
    return {"message": "Password updated successfully"}

@app.put("/cart/{user_id}/{product_id}", tags=["Update (PUT)"])
async def update_cart_quantity(user_id: str, product_id: str, quantity: int = Query(gt=0), current_user: dict = Depends(get_current_user)):
    if current_user["user_id"] != user_id and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    result = await app.database.cart.update_one(
        {"product_id": product_id, "user_id": user_id},
        {"$set": {"quantity": quantity}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found in cart")
    return {"message": "Quantity updated successfully"}

@app.put("/orders/{user_id}/{order_id}", tags=["Update (PUT)"])
async def update_order_items(user_id: str, order_id: str, product_id: str, new_quantity: int = Query(gt=0), current_user: dict = Depends(get_current_user)):
    if current_user["user_id"] != user_id and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
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
# DELETE
# ==========================================

@app.delete("/users/{user_id}", tags=["Delete (DELETE)"])
async def delete_account(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["user_id"] != user_id and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    try:
        user_obj_id = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid User ID")
    await app.database.users.delete_one({"_id": user_obj_id})
    await app.database.cart.delete_many({"user_id": user_id})
    await app.database.orders.delete_many({"user_id": user_id})
    return {"message": "Account permanently deleted"}

@app.delete("/cart/{user_id}/{product_id}", tags=["Delete (DELETE)"])
async def delete_from_cart(user_id: str, product_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["user_id"] != user_id and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    result = await app.database.cart.delete_one({"product_id": product_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    return {"message": "Item removed from cart"}

@app.delete("/orders/{user_id}/{order_id}", tags=["Delete (DELETE)"])
async def delete_order(user_id: str, order_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["user_id"] != user_id and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    try:
        order_obj_id = ObjectId(order_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Order ID")
    result = await app.database.orders.delete_one({"_id": order_obj_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}

# ==========================================
# ADMIN
# ==========================================

@app.get("/admin/carts", tags=["Admin"])
async def admin_get_all_carts(current_user: dict = Depends(require_admin)):
    users = await app.database.users.find({"role": "user"}).to_list(1000)

    result_users = []
    total_cart_items = 0
    total_cart_value = 0
    total_order_value = 0

    for user in users:
        user_id = str(user["_id"])

        cart_items = await app.database.cart.find({"user_id": user_id}).to_list(100)
        orders = await app.database.orders.find({"user_id": user_id}).to_list(100)

        formatted_cart_items = []
        user_cart_total = 0
        user_cart_quantity = 0

        for item in cart_items:
            item["_id"] = str(item["_id"])
            item_quantity = item.get("quantity", 0)
            item_price = item.get("price", 0)
            item_subtotal = item_price * item_quantity

            item["subtotal"] = item_subtotal

            formatted_cart_items.append(item)
            user_cart_total += item_subtotal
            user_cart_quantity += item_quantity

        formatted_orders = []
        user_order_total = 0

        for order in orders:
            order["_id"] = str(order["_id"])

            if "created_at" in order and hasattr(order["created_at"], "isoformat"):
                order["created_at"] = order["created_at"].isoformat()

            for item in order.get("items", []):
                if "_id" in item:
                    item["_id"] = str(item["_id"])

            user_order_total += order.get("total_price", 0)
            formatted_orders.append(order)

        total_cart_items += user_cart_quantity
        total_cart_value += user_cart_total
        total_order_value += user_order_total

        result_users.append({
            "user_id": user_id,
            "username": user.get("username"),
            "email": user.get("email"),
            "cart": {
                "items": formatted_cart_items,
                "total_items": user_cart_quantity,
                "total_value": user_cart_total
            },
            "orders": formatted_orders,
            "order_total_value": user_order_total
        })

    return {
        "total_users": len(result_users),
        "total_cart_items": total_cart_items,
        "total_cart_value": total_cart_value,
        "total_order_value": total_order_value,
        "users": result_users
    }