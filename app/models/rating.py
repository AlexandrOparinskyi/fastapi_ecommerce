from sqlalchemy import Column, Integer, Boolean, ForeignKey, Float

from app.backend.db import Base


class Rating(Base):
    __tablename__ = 'rating'

    id = Column(Integer, primary_key=True, index=True)
    grade = Column(Float, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    is_active = Column(Boolean, default=True)
