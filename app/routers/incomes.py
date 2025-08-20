from fastapi import APIRouter, HTTPException
from app.database import db
from app.schemas import IncomeCreate
from bson import ObjectId
from datetime import datetime, timedelta,date
from typing import Literal, Optional
from app.database import incomes_collection, expenses_collection, users_collection


router = APIRouter(prefix="/incomes", tags=["Incomes"])

incomes_collection = db["incomes"]
users_collection = db["users"]

# הוספת הכנסה
@router.post("/{user_id}/add")
async def add_income(user_id: str, income: IncomeCreate):
    if income.amount < 0:
        raise HTTPException(status_code=400, detail="Income amount cannot be negative")

    income_doc = income.dict()
    income_doc["user_id"] = ObjectId(user_id)
    
    # המרה ל־datetime לפני שמירה, עם שעה 00:00:00
    income_doc["date"] = datetime.combine(income.date, datetime.min.time())

    await incomes_collection.insert_one(income_doc)
    return {"status": "success", "message": "Income added"}

def convert_object_ids(data):
    for item in data:
        item["_id"] = str(item["_id"])  # המר את ה־_id למחרוזת
        item["user_id"] = str(item["user_id"])  # המר את ה־user_id למחרוזת
        if isinstance(item["date"], datetime):
            item["date"] = item["date"].isoformat()  # המר תאריך לטקסט קריא
    return data

# קבלת כל ההכנסות לפי חודש ושנה
@router.get("/{user_id}")
async def get_incomes(user_id: str, year: int = None, month: int = None):
    query = {"user_id": ObjectId(user_id)}

    if year and month:
        try:
            start = datetime(year, month, 1)
            end = datetime(year + (1 if month == 12 else 0), (month % 12) + 1, 1)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid month/year combination")
        query["date"] = {"$gte": start, "$lt": end}

    results = await incomes_collection.find(query).to_list(length=None)
    if not results:
        raise HTTPException(status_code=404, detail="No income data found for the given period")
    return convert_object_ids(results)

# עדכון הכנסה
@router.put("/{user_id}/{income_id}")
async def update_income(user_id: str, income_id: str, updated: IncomeCreate):
    if updated.amount < 0:
        raise HTTPException(status_code=400, detail="Income amount cannot be negative")

    data = updated.dict()
    if isinstance(data["date"], date) and not isinstance(data["date"], datetime):
        # הפוך ל־datetime מלא (שעה 00:00)
        data["date"] = datetime.combine(data["date"], datetime.min.time())

    result = await incomes_collection.update_one(
        {"_id": ObjectId(income_id), "user_id": ObjectId(user_id)},
        {"$set": data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Income not found or unchanged")
    return {"status": "success", "message": "Income updated"}


# קבלת סך החיסכון לתקופה
@router.get("/{user_id}/saving-summary")
async def get_saving_summary(user_id: str, period: Literal["1month", "3months", "6months", "12months"] = "1month"):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    months = int(period.replace("month", "").replace("s", ""))
    end = datetime.utcnow()
    start = end - timedelta(days=30 * months)

    # שליפת הכנסות
    income_query = {
        "user_id": ObjectId(user_id),
        "date": {"$gte": start, "$lte": end}
    }
    incomes = await incomes_collection.find(income_query).to_list(length=None)
    total_income = sum(i["amount"] for i in incomes)

    # שליפת הוצאות
    expense_query = {
        "user_id": ObjectId(user_id),
        "date": {"$gte": start, "$lte": end}
    }
    expenses = await expenses_collection.find(expense_query).to_list(length=None)
    total_expenses = sum(e["amount"] for e in expenses)

    # חישוב חיסכון בפועל
    net_saved = total_income - total_expenses

    return {
        "period_start": start.date(),  # הצגה יפה
        "period_end": end.date(),
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_saved": round(net_saved, 2)
    }

# מחיקת הכנסה
@router.delete("/{user_id}/{income_id}")
async def delete_income(user_id: str, income_id: str):
    result = await incomes_collection.delete_one({
        "_id": ObjectId(income_id),
        "user_id": ObjectId(user_id)
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Income not found")
    return {"status": "success", "message": "Income deleted"}
