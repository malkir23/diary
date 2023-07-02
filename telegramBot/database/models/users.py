from sqlalchemy import Integer, VARCHAR, Boolean, Column, DateTime
from datetime import datetime
from .. base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(32), unique=False, nullable=False)
    admin = Column(Boolean, default=False)

    created_at = Column(DateTime, default=lambda: datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # def __repr__(self) -> str:
    #     return f'<User {self.name}>'
