from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, ARRAY, JSON
from sqlalchemy.dialects.postgresql import JSONB
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
    page_reference = Column(JSONB)  # {file_path: str, page_numbers: int, y_coord: float}
    price_data = Column(JSONB)  # {processed_at: datetime, catalog_version: str, tables: [{page_num: int, bbox: tuple, price_data: list}]}
    sequence_number = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.now)