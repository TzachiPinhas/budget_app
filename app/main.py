from fastapi import FastAPI
from app.routers import users
from app.routers import incomes
from app.routers import expenses

from app.database import db
import os
from dotenv import load_dotenv

load_dotenv()  

app = FastAPI(title="Budget API")

app.include_router(users.router)
app.include_router(incomes.router)
app.include_router(expenses.router)


@app.get("/")
async def root():
    return {"status": "ok", "message": "Budget API is running"}

@app.get("/test-mongo")
async def test_mongo():
    try:
        collections = await db.list_collection_names()
        return {"status": "ok", "collections": collections}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
