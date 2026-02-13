"""
analytics_service.py

Contains database query logic for analytics.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from models import ChatHistory, TokenAnalytics


# =====================================================
# MOST ASKED QUESTIONS (GLOBAL)
# =====================================================

def most_asked_questions(db: Session):

    results = (
        db.query(
            ChatHistory.message,
            func.count(ChatHistory.message).label("count")
        )
        .filter(ChatHistory.role == "user")
        .group_by(ChatHistory.message)
        .order_by(func.count(ChatHistory.message).desc())
        .all()
    )

    return [
        {
            "message": row.message,
            "count": row.count
        }
        for row in results
    ]


# =====================================================
# TOKEN SUMMARY (GLOBAL - ADMIN)
# =====================================================

def token_summary(db: Session):

    result = (
        db.query(
            func.sum(TokenAnalytics.prompt_tokens).label("total_prompt_tokens"),
            func.sum(TokenAnalytics.completion_tokens).label("total_completion_tokens"),
            func.sum(TokenAnalytics.total_tokens).label("grand_total_tokens"),
            func.sum(TokenAnalytics.total_cost).label("total_cost")  # ✅ FIXED
        )
        .first()
    )

    return {
        "total_prompt_tokens": result.total_prompt_tokens or 0,
        "total_completion_tokens": result.total_completion_tokens or 0,
        "grand_total_tokens": result.grand_total_tokens or 0,
        "total_cost": float(result.total_cost or 0.0),
    }


# =====================================================
# TOKEN SUMMARY (PER USER)
# =====================================================
def token_summary_by_user(db: Session, user_email: str):

    result = (
        db.query(
            func.sum(TokenAnalytics.prompt_tokens).label("total_prompt_tokens"),
            func.sum(TokenAnalytics.completion_tokens).label("total_completion_tokens"),
            func.sum(TokenAnalytics.total_tokens).label("grand_total_tokens"),
            func.sum(TokenAnalytics.total_cost).label("total_cost"),
        )
        .join(TokenAnalytics.user)
        .filter(TokenAnalytics.user.has(email=user_email))
        .first()
    )

    return {
        "total_prompt_tokens": result.total_prompt_tokens or 0,
        "total_completion_tokens": result.total_completion_tokens or 0,
        "grand_total_tokens": result.grand_total_tokens or 0,
        "total_cost": float(result.total_cost or 0.0),
    }

# =====================================================
# ALL TOKEN RECORDS (ADMIN)
# =====================================================

def get_all_token_records(db: Session):

    records = db.query(TokenAnalytics).all()

    return [
        {
            "id": record.id,
            "user_email": record.user_email,
            "prompt_tokens": record.prompt_tokens,
            "completion_tokens": record.completion_tokens,
            "total_tokens": record.total_tokens,
            "total_cost": record.total_cost,  # ✅ FIXED
            "created_at": record.timestamp
        }
        for record in records
    ]
