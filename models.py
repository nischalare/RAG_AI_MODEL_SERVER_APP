"""
models.py

Defines all database models (tables) used in the system.

We use SQLAlchemy ORM to:
- Define database structure
- Create relationships
- Enforce constraints
- Support analytics tracking

Tables:
1. User
2. ChatHistory
3. TokenAnalytics
"""

# =====================================================
# IMPORTS
# =====================================================

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Float,
    Index
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

# Base class required by SQLAlchemy
Base = declarative_base()


# =====================================================
# USER MODEL
# =====================================================

class User(Base):
    """
    Represents a registered user in the system.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String(255), unique=True, nullable=False, index=True)

    password = Column(String(255), nullable=False)

    role = Column(String(50), default="USER", nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # One user → many chat messages
    chats = relationship(
        "ChatHistory",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # One user → many analytics records
    analytics = relationship(
        "TokenAnalytics",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


# =====================================================
# CHAT HISTORY MODEL
# =====================================================

class ChatHistory(Base):
    """
    Stores every message exchanged in a conversation.
    """

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    session_id = Column(String(100), index=True)

    role = Column(String(20), nullable=False)  # "user" or "bot"

    message = Column(Text, nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationship back to User
    user = relationship("User", back_populates="chats")

    # Composite index for faster session queries
    __table_args__ = (
        Index("ix_chat_user_session", "user_id", "session_id"),
    )

    def __repr__(self):
        return (
            f"<ChatHistory(user_id={self.user_id}, "
            f"session_id={self.session_id}, role={self.role})>"
        )


# =====================================================
# TOKEN ANALYTICS MODEL (ENTERPRISE FINAL VERSION)
# =====================================================

class TokenAnalytics(Base):
    """
    Stores token usage information for cost monitoring.

    Tracks:
    - Prompt tokens
    - Completion tokens
    - Total tokens
    - Cost
    - Per-user usage
    """

    __tablename__ = "token_analytics"

    id = Column(Integer, primary_key=True, index=True)

    # Link analytics to specific user
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Session identifier
    session_id = Column(String(100), index=True)

    # Token tracking
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)

    # AI cost tracking (PostgreSQL = double precision)
    total_cost = Column(Float, default=0.0, nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationship back to User
    user = relationship("User", back_populates="analytics")

    # Composite index for analytics performance
    __table_args__ = (
        Index("ix_analytics_user_session", "user_id", "session_id"),
    )

    def __repr__(self):
        return (
            f"<TokenAnalytics(user_id={self.user_id}, "
            f"session_id={self.session_id}, "
            f"total_tokens={self.total_tokens}, "
            f"total_cost={self.total_cost})>"
        )
