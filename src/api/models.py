from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, ARRAY, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    product_name = Column(String)
    brand_name = Column(String)
    designer = Column(String)
    year = Column(Integer)
    type_of_product = Column(String)
    all_colors = Column(ARRAY(String))
    page_reference = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow) 