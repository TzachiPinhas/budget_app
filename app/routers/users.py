from fastapi import APIRouter, HTTPException
from app.schemas import UserRegister, UserLogin
from app.utils import hash_password, verify_password
from app.database import db

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register")
async def register_user(user: UserRegister):
    users_collection = db["users"]
    existing = await users_collection.find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed = hash_password(user.password)
    await users_collection.insert_one({
        "username": user.username,
        "password": hashed
    })
    return {"status": "success", "message": "User registered successfully"}

@router.post("/login")
async def login_user(user: UserLogin):
    users_collection = db["users"]
    existing = await users_collection.find_one({"username": user.username})
    if not existing or not verify_password(user.password, existing["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "status": "success",
        "message": f"Welcome back, {user.username}!",
        "user_id": str(existing["_id"])
    }