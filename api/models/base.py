from sqlalchemy.orm import declarative_base
import datetime
import sqlalchemy as sa

Base = declarative_base()


class TimestampMixin:
    created_at = sa.Column(sa.DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )
