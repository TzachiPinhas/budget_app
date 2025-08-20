from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import os


MONGO_URL = os.getenv("MONGO_URL")

client = AsyncIOMotorClient(MONGO_URL, server_api=ServerApi('1'))
db = client["budget_db"]

# אוספים
users_collection = db["users"]
incomes_collection = db["incomes"]
expenses_collection = db["expenses"]
categories_collection = db["categories"]
