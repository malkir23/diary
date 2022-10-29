from sqlalchemy import Integer, String, Boolean, Column, DateTime
from db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    admin = Column(Boolean, default=False)


class WorkCalendar(Base):
    __tablename__ = 'work_calendar'

    id = Column(Integer, primary_key=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    name_work = Column(String)
    user_id = Column(String)