from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)

    tasks = relationship("Task", back_populates="category")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False)  # "todo", "in_progress", "done"
    type = Column(String, nullable=False)  # "pre_flight", "in_flight", "post_flight"
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    result = Column(String, nullable=True)

    category = relationship("Category", back_populates="tasks")
