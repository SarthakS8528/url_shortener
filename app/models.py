
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base


class URL(Base):

    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)

    original_url = Column(Text, nullable=False)

    short_code = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    is_active = Column(Boolean, default=True)

    # One URL can have multiple clicks
    clicks = relationship(
        "Click",
        back_populates="url",
        cascade="all, delete-orphan"
    )
    description=Column(String(255),nullable=True)


class Click(Base):

    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, index=True)

    url_id = Column(
        Integer,
        ForeignKey("urls.id", ondelete="CASCADE"),
        nullable=False
    )

    clicked_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    ip_address = Column(String(45), nullable=True)

    # Each click belongs to one URL
    url = relationship(
        "URL",
        back_populates="clicks"
    )
