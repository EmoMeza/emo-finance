from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, periods, categories, expenses, expense_templates

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(periods.router, prefix="/periods", tags=["Periods"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
api_router.include_router(expense_templates.router, prefix="/expense-templates", tags=["Expense Templates"])


@api_router.get("/status")
async def api_status():
    return {"status": "API v1 is running"}
