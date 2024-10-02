from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from app.backend.db import Base

from datetime import datetime


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    rating_id = Column(Integer, ForeignKey('rating.id'))
    comment = Column(String)
    comment_date = Column(DateTime, default=datetime.now())
    is_active = Column(Boolean, default=True)
