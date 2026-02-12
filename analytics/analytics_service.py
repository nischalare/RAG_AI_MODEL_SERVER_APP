"""
analytics_service.py

Contains database query logic for analytics.
No FastAPI routes here.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from models import ChatHistory, TokenAnalytics


# =====================================================
# MOST ASKED QUESTIONS (GLOBAL)
# =====================================================

def most_asked_questions(db: Session):
    """
    Returns most frequently asked user questions globally.
    """

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
# TOKEN USAGE SUMMARY (GLOBAL)
# =====================================================

def token_summary(db: Session):
    """
    Returns total token usage statistics (global).
    """

    result = (
        db.query(
            func.sum(TokenAnalytics.prompt_tokens).label("total_prompt_tokens"),
            func.sum(TokenAnalytics.completion_tokens).label("total_completion_tokens"),
            func.sum(TokenAnalytics.total_tokens).label("grand_total_tokens")
        )
        .first()
    )

    return {
        "total_prompt_tokens": result.total_prompt_tokens or 0,
        "total_completion_tokens": result.total_completion_tokens or 0,
        "grand_total_tokens": result.grand_total_tokens or 0,
    }


# =====================================================
# TOKEN USAGE SUMMARY (PER USER)
# =====================================================

def token_summary_by_user(db: Session, user_email: str):
    """
    Returns token usage statistics for a specific user.
    """

    result = (
        db.query(
            func.sum(TokenAnalytics.prompt_tokens).label("total_prompt_tokens"),
            func.sum(TokenAnalytics.completion_tokens).label("total_completion_tokens"),
            func.sum(TokenAnalytics.total_tokens).label("grand_total_tokens")
        )
        .filter(TokenAnalytics.user_email == user_email)
        .first()
    )

    return {
        "total_prompt_tokens": result.total_prompt_tokens or 0,
        "total_completion_tokens": result.total_completion_tokens or 0,
        "grand_total_tokens": result.grand_total_tokens or 0,
    }


# =====================================================
# ALL TOKEN RECORDS
# =====================================================

def get_all_token_records(db: Session):
    """
    Returns all token analytics records formatted as dictionaries.
    """

    records = db.query(TokenAnalytics).all()

    return [
        {
            "id": record.id,
            "user_email": record.user_email,
            "prompt_tokens": record.prompt_tokens,
            "completion_tokens": record.completion_tokens,
            "total_tokens": record.total_tokens,
            "cost": record.cost,
            "created_at": record.created_at
        }
        for record in records
    ]
