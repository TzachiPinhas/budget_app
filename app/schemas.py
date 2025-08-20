from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


# ========== סכמות למשתמשים ==========

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class SavingPercentUpdate(BaseModel):
    percent: float = Field(..., ge=0, le=100)

# ========== סכמות להכנסות ==========

class IncomeCreate(BaseModel):
    amount: float = Field(..., gt=0)
    date: date
    source: str = Field(default="other")  # למשל: משכורת, מלגה, מכירת מוצר וכו'

class IncomeUpdate(BaseModel):
    amount: float = Field(..., gt=0)
    date: date
    source: str = Field(default="other")



# ========== סכמות להוצאות ==========


class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Expense amount must be positive")
    category: str = Field(..., min_length=1, max_length=50)
    date: date 
    note: Optional[str] = Field(None, max_length=200)

    class Config:
        schema_extra = {
            "example": {
                "amount": 120.5,
                "category": "Groceries",
                "date": "2025-08-14T00:00:00Z",
                "note": "Weekly supermarket run"
            }
        }

class ExpenseInDB(ExpenseCreate):
    id: str = Field(..., alias="_id")
    user_id: str