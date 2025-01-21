from sqlalchemy import create_engine, or_, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Optional
from .models import Base, Product
from .config import DATABASE_URL
from pathlib import Path
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
    
    def add_products(self, products: List[dict]):
        """Add products with sequence numbers"""
        try:
            product_models = [Product(**product) for product in products]
            self.session.add_all(product_models)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error adding products: {str(e)}")
            raise
    
    def get_product(self, product_id: int) -> Optional[Dict]:
        try:
            product = self.session.query(Product).filter(Product.id == product_id).first()
            return self._product_to_dict(product) if product else None
        except SQLAlchemyError as e:
            logging.error(f"Error getting product: {str(e)}")
            raise
    
    def search(self, query: str = None, pdf: str = None) -> List[Dict]:
        """Search products with optional PDF filter"""
        try:
            # Start with base query
            db_query = self.session.query(Product)
            
            # Add PDF filter if provided
            if pdf:
                db_query = db_query.filter(
                    Product.page_reference['file_path'].astext == pdf
                )
            
            # Add search conditions if query exists
            if query:
                try:
                    year_query = int(query)
                    year_filter = Product.year == year_query
                except ValueError:
                    year_filter = False

                search_filter = or_(
                    Product.product_name.ilike(f'%{query}%'),
                    Product.brand_name.ilike(f'%{query}%'),
                    Product.designer.ilike(f'%{query}%'),
                    Product.type_of_product.ilike(f'%{query}%'),
                    Product.all_colors.any(query),
                    year_filter if year_filter else False
                )
                db_query = db_query.filter(search_filter)
            
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
            'page_reference': product.page_reference or {}, # Ensure it's never null
            'price_data': product.price_data or {},
            'sequence_number': product.sequence_number
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

    def pdf_exists(self, filename: str) -> bool:
        """Check if any products exist from this PDF"""
        return self.session.query(Product).filter(
            Product.page_reference['file_path'].astext == filename
        ).count() > 0
    
    def find_products(self, name: str, brand: str, type: str) -> List[Product]:
        """Find products matching name, brand and type"""
        return self.session.query(Product).filter(
            Product.product_name.ilike(name),
            Product.brand_name.ilike(f"%{brand}%"),
            Product.type_of_product.ilike(f"%{type}%")
        ).all()
    
    def get_next_product(self, current_product: Product) -> Optional[Product]:
        """Get next product in same PDF by sequence number"""
        return self.session.query(Product).filter(
            Product.page_reference['file_path'].astext == current_product.page_reference['file_path'],
            Product.sequence_number == current_product.sequence_number + 1
        ).first()
    
    def update_price_data(self, product_id: int, price_data: dict):
        """Update price data for a product"""
        try:
            product = self.session.query(Product).get(product_id)
            if product:
                product.price_data = price_data
                self.session.commit()
                logger.info(f"Updated price data for product {product_id}")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating price data: {str(e)}")
            raise

def reset_database(environment: str = 'local'):
    " Drop all tables and recreate with new schema. environment = local or cloud "
    try:
        logger.info(f"Resetting {environment} database...")
        print("Resetting database...")
        
        # Select database URL based on environment
        if environment == 'local':
            db_url = 'postgresql://bayek:userbayek@localhost:5432/pdfmagic'
        elif environment == 'cloud':
            # db_url = os.getenv('CLOUD_DATABASE_URL')  # Get from .env file
            db_url = 'postgresql://postgres:user123@/smartcatalog?host=/cloudsql/key-being-442223-h1:europe-west1:smartcatalog-db'
        else:
            raise ValueError(f"Unknown environment: {environment}")
            
        engine = create_engine(db_url)
        
        # Drop all existing tables
        Base.metadata.drop_all(engine)
        logger.info(f"Dropped all existing tables from {environment} database")
        
        # Create new tables with updated schema
        Base.metadata.create_all(engine)
        logger.info(f"Created new tables in {environment} database")
        
    except Exception as e:
        logger.error(f"Error resetting {environment} database: {str(e)}")
        raise

if __name__ == "__main__":
    import sys
    env = sys.argv[1] if len(sys.argv) > 1 else 'local'
    reset_database(env)