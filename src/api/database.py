from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Optional
from .models import Base, Product
from .config import DATABASE_URL
import logging
import os
import json

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
    
    def search(self, query: str, category: Optional[str] = None) -> List[Dict]:
        try:
            # Start with base query
            db_query = self.session.query(Product)
            
            # Add search conditions
            if query:
                search_filter = or_(
                    Product.product_name.ilike(f'%{query}%'),
                    Product.brand_name.ilike(f'%{query}%'),
                    Product.designer.ilike(f'%{query}%'),
                    Product.type_of_product.ilike(f'%{query}%')
                )
                db_query = db_query.filter(search_filter)
            
            # Add category filter
            if category:
                db_query = db_query.filter(Product.type_of_product.ilike(f'%{category}%'))
                        
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
            'product_name': product.product_name,
            'brand_name': product.brand_name,
            'designer': product.designer,
            'year': product.year,
            'type_of_product': product.type_of_product,
            'all_colors': product.all_colors or [], # Ensure it's never null
            'page_reference': product.page_reference or {} # Ensure it's never null
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

    def import_from_json(self, json_file_path: str) -> Dict:
        """Import products from a JSON file"""
        try:
            logger.info(f"Reading JSON file from: {json_file_path}")
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            furniture_items = data.get('furnitureItems', [])
            logger.info(f"Found {len(furniture_items)} items to import")
            
            added_count = 0
            
            for item in furniture_items:
                try:
                    product = Product(
                        product_name=item.get('product_name'),
                        brand_name=item.get('brand_name'),
                        designer=item.get('designer'),
                        year=item.get('year'),
                        type_of_product=item.get('type_of_product'),
                        all_colors=item.get('all_colors', []),
                        page_reference=item.get('page_reference', {})
                    )
                    self.session.add(product)
                    added_count += 1
                except Exception as e:
                    logger.error(f"Error adding product: {str(e)}")
                    raise
            
            self.session.commit()
            logger.info(f"Successfully imported {added_count} products")
            return {"message": f"Successfully imported {added_count} products"}
            
        except Exception as e:
            self.session.rollback()
            logging.error(f"Error importing JSON: {str(e)}")
            # Re-raise the exception after rollback
            raise
