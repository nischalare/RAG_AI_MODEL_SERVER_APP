from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from auth.dependencies import get_current_user
from database import SessionLocal
from models import TokenAnalytics
from analytics.analytics_service import (
    most_asked_questions,
    token_summary,
    token_summary_by_user,
    get_all_token_records
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# ================================
# DB Dependency
# ================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================================
# USER ANALYTICS (PER USER)
# ================================
@router.get("/summary")
def user_analytics_summary(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user_email = current_user["sub"]

    summary = token_summary_by_user(db, user_email)

    return {
        "total_tokens": summary["grand_total_tokens"],
        "total_prompt_tokens": summary["total_prompt_tokens"],
        "total_completion_tokens": summary["total_completion_tokens"],
        "total_cost": round(summary["total_cost"], 6),
    }

# ================================
# ADMIN ANALYTICS (GLOBAL)
# ================================
@router.get("/admin")
def admin_analytics(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin-only analytics
    """

    if current_user["role"] != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    summary = token_summary(db)

    return {
        "most_asked_questions": most_asked_questions(db),
        "token_summary": summary,
        "all_token_records": get_all_token_records(db)
    }


