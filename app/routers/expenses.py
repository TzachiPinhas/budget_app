from fastapi import APIRouter, HTTPException
from app.database import db
from app.schemas import ExpenseCreate
from bson import ObjectId
from datetime import datetime, timedelta ,date
from typing import Literal, Optional

router = APIRouter(prefix="/expenses", tags=["Expenses"])

expenses_collection = db["expenses"]

# -------------------------------
# הוספת הוצאה
@router.post("/{user_id}/add")
async def add_expense(user_id: str, expense: ExpenseCreate):
    if expense.amount < 0:
        raise HTTPException(status_code=400, detail="Expense amount cannot be negative")

    expense_doc = expense.dict()
    expense_doc["user_id"] = ObjectId(user_id)

    # המרה מ-date ל-datetime כדי ש-MongoDB יוכל לשמור את זה
    if isinstance(expense_doc["date"], date):
        expense_doc["date"] = datetime.combine(expense_doc["date"], datetime.min.time())

    await expenses_collection.insert_one(expense_doc)
    return {"status": "success", "message": "Expense added"}

# -------------------------------

# שליפת הוצאות לפי חודש/שנה ואופציונלית לפי קטגוריה (הכל כמחרוזות)
@router.get("/{user_id}")
async def get_expenses(
    user_id: str,
    year: Optional[str] = None,
    month: Optional[str] = None,
    category: Optional[str] = None
):
    query = {"user_id": ObjectId(user_id)}

    if year and month:
        try:
            year_int = int(year)
            month_int = int(month)
            start = datetime(year_int, month_int, 1)
            end = datetime(year_int + (1 if month_int == 12 else 0), (month_int % 12) + 1, 1)
            query["date"] = {"$gte": start, "$lt": end}
        except ValueError:
            raise HTTPException(status_code=400, detail="Year and month must be valid integers")

    if category:
        query["category"] = category

    results = await expenses_collection.find(query).to_list(length=None)

    if not results:
        raise HTTPException(status_code=404, detail="No expenses found for the given criteria")

    # המרת תוצאות: ObjectId -> str, date -> str (או date בלבד)
    for expense in results:
        expense["_id"] = str(expense["_id"])
        expense["user_id"] = str(expense["user_id"])
        if isinstance(expense["date"], datetime):
            expense["date"] = expense["date"].date().isoformat()  # או פשוט expense["date"].date()

    return results


# -------------------------------
# עדכון הוצאה
from datetime import datetime, time

@router.put("/{user_id}/{expense_id}")
async def update_expense(user_id: str, expense_id: str, updated: ExpenseCreate):
    if updated.amount < 0:
        raise HTTPException(status_code=400, detail="Expense amount cannot be negative")

    # המרת date ל־datetime (ללא שעה)
    updated_data = updated.dict()
    updated_data["date"] = datetime.combine(updated.date, time.min)

    result = await expenses_collection.update_one(
        {"_id": ObjectId(expense_id), "user_id": ObjectId(user_id)},
        {"$set": updated_data}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found or unchanged")

    return {"status": "success", "message": "Expense updated"}


# -------------------------------
# מחיקת הוצאה
@router.delete("/{user_id}/{expense_id}")
async def delete_expense(user_id: str, expense_id: str):
    result = await expenses_collection.delete_one({
        "_id": ObjectId(expense_id),
        "user_id": ObjectId(user_id)
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"status": "success", "message": "Expense deleted"}

# -------------------------------
# סיכום הוצאות לפי תקופה
@router.get("/{user_id}/summary")
async def get_expense_summary(user_id: str, period: Literal["1month", "3months", "6months", "12months"] = "1month"):
    months = int(period.replace("month", "").replace("s", ""))
    end = datetime.utcnow()
    start = end - timedelta(days=30 * months)

    query = {"user_id": ObjectId(user_id), "date": {"$gte": start, "$lte": end}}
    expenses = await expenses_collection.find(query).to_list(length=None)

    if not expenses:
        raise HTTPException(status_code=404, detail="No expense data available for that period")

    total_expenses = sum(e["amount"] for e in expenses)

    return {
        "period_start": start,
        "period_end": end,
        "total_expenses": total_expenses,
        "num_expenses": len(expenses)
    }
