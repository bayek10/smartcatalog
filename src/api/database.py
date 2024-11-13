from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Optional
from .models import Base, Product
from .config import DATABASE_URL
import logging
import os

logger = logging.getLogger(__name__)

class DatabaseSession:
    def __init__(self):
        self.Session = None
        self.engine = None
        
    def __call__(self):
        if self.Session is None:
            self.init_db()
        return self.Session()
    
    def init_db(self):
        try:
            logger.info("Initializing database connection...")
            self.engine = create_engine(DATABASE_URL)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

db_session = DatabaseSession()

class ProductDB:
    def __init__(self):
        self.session = db_session()
    
    def add_products(self, products: List[Dict]):
        try:
            for product_data in products:
                product = Product(
                    name=product_data.get('name'),
                    brand=product_data.get('brand'),
                    product_type=product_data.get('type'),
                    dimensions=product_data.get('dimensions'),
                    price=float(product_data.get('price', 0)) if product_data.get('price') else None,
                    text_content=product_data.get('text_content'),
                    source_pdf=product_data.get('source_pdf'),
                    page_number=product_data.get('page_number')
                )
                self.session.add(product)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            logging.error(f"Error adding products: {str(e)}")
            raise
    
    def get_product(self, product_id: int) -> Optional[Dict]:
        try:
            product = self.session.query(Product).filter(Product.id == product_id).first()
            return self._product_to_dict(product) if product else None
        except SQLAlchemyError as e:
            logging.error(f"Error getting product: {str(e)}")
            raise
    
    def search(self, query: str, category: Optional[str] = None, 
              min_price: Optional[float] = None, max_price: Optional[float] = None) -> List[Dict]:
        try:
            # Start with base query
            db_query = self.session.query(Product)
            
            # Add search conditions
            if query:
                search_filter = or_(
                    Product.name.ilike(f'%{query}%'),
                    Product.brand.ilike(f'%{query}%'),
                    Product.product_type.ilike(f'%{query}%'),
                    Product.text_content.ilike(f'%{query}%')
                )
                db_query = db_query.filter(search_filter)
            
            # Add category filter
            if category:
                db_query = db_query.filter(Product.product_type.ilike(f'%{category}%'))
            
            # Add price range filters
            if min_price is not None:
                db_query = db_query.filter(Product.price >= min_price)
            if max_price is not None:
                db_query = db_query.filter(Product.price <= max_price)
            
            # Execute query and convert results to dict
            products = db_query.all()
            return [self._product_to_dict(p) for p in products]
            
        except SQLAlchemyError as e:
            logging.error(f"Error searching products: {str(e)}")
            raise

    def get_all_products(self) -> List[Dict]:
        try:
            products = self.session.query(Product).all()
            return [self._product_to_dict(p) for p in products]
        except SQLAlchemyError as e:
            logging.error(f"Error fetching all products: {str(e)}")
            raise

    def _product_to_dict(self, product: Product) -> Dict:
        return {
            'id': product.id,
            'name': product.name,
            'brand': product.brand,
            'type': product.product_type,
            'dimensions': product.dimensions,
            'price': str(product.price) if product.price else None,
            'text_content': product.text_content,
            'source_pdf': product.source_pdf,
            'page_number': product.page_number
        }

    def clear_products(self):
        try:
            logger.info("Attempting to clear all products from database...")
            self.session.query(Product).delete()
            self.session.commit()
            logger.info("Successfully cleared all products")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error clearing products: {str(e)}")
            raise
