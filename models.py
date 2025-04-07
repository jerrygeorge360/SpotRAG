from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Enum, Integer, DateTime, ForeignKey, SmallInteger, UniqueConstraint
from sqlalchemy.sql import func
from flask_login import UserMixin

from enumprop import Providers


class Base(DeclarativeBase):
    ...



db = SQLAlchemy(model_class=Base)


class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement="auto")
    oauth_provider: Mapped[Providers] = mapped_column(Enum(Providers), nullable=False, default=Providers.SPOTIFY)
    oauth_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False)
    profile_image_url: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'profile_image': self.profile_image_url,
            'created_at': self.created_at.isoformat()  # Convert datetime to ISO format string
        }
