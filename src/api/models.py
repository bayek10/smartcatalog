from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    brand = Column(String)
    product_type = Column(String)
    dimensions = Column(String)
    price = Column(Float)
    text_content = Column(String)
    source_pdf = Column(String)
    page_number = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow) 