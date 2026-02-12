"""
analytics_router.py

Defines analytics endpoints for:
1. Normal users  → /analytics/summary
2. Admin users   → /analytics/admin
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import SessionLocal
from analytics.analytics_service import (
    most_asked_questions,
    token_summary,
    get_all_token_records
)

# =====================================================
# ROUTER CONFIG
# =====================================================

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

# =====================================================
# DB Dependency
# =====================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =====================================================
# USER ANALYTICS SUMMARY
# =====================================================

@router.get("/summary")
def user_analytics_summary(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns token usage summary for logged-in user.
    Accessible to all authenticated users.
    """

    summary = token_summary(db) or {}

    return {
        "total_tokens": summary.get("grand_total_tokens", 0),
        "total_prompt_tokens": summary.get("total_prompt_tokens", 0),
        "total_completion_tokens": summary.get("total_completion_tokens", 0),
    }


# =====================================================
# ADMIN ANALYTICS ENDPOINT
# =====================================================

@router.get("/admin")
def admin_analytics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns full analytics data.
    Only accessible to ADMIN users.
    """

    # 🔐 Role Check
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    summary = token_summary(db) or {}

    return {
        "most_asked_questions": most_asked_questions(db),
        "token_summary": {
            "total_prompt_tokens": summary.get("total_prompt_tokens", 0),
            "total_completion_tokens": summary.get("total_completion_tokens", 0),
            "grand_total_tokens": summary.get("grand_total_tokens", 0),
        },
        "all_token_records": get_all_token_records(db)
    }
