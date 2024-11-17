from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect
from typing import Optional
from .database import ProductDB, db_session
from .models import Base
from ..pdf_processor import PDFProcessor
import tempfile
import os
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    db_session.init_db()
    yield
    # Shutdown: Close database session
    if db.session:
        db.session.close()

app = FastAPI(lifespan=lifespan)
db = ProductDB()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create PDF directory (use absolute path for clarity)
PDF_STORAGE_PATH = "pdfs"  # or "public/pdfs" if you prefer that structure
os.makedirs(PDF_STORAGE_PATH, exist_ok=True)

# Mount the PDF directory
app.mount("/pdfs", StaticFiles(directory=PDF_STORAGE_PATH), name="pdfs")

@app.get("/search")
async def search_products(
    query: str,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    results = db.search(
        query=query,
        category=category,
        min_price=min_price,
        max_price=max_price
    )
    return results

@app.get("/product/{product_id}")
async def get_product(product_id: str):
    return db.get_product(product_id)

@app.get("/debug/products")
async def get_all_products():
    try:
        products = db.get_all_products()
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/debug/products")
async def clear_all_products():
    try:
        db.clear_products()
        return {"message": "All products cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    
    with open(temp_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Process PDF
    processor = PDFProcessor(temp_path)
    products = processor.extract_product_info()
    
    # Store in database
    db.add_products(products)
    
    # Cleanup
    os.remove(temp_path)
    os.rmdir(temp_dir)
    
    return {"message": f"Processed {len(products)} products from {file.filename}"}

@app.post("/import-json")
async def import_json_data(file: UploadFile = File(...)):
    """Import furniture data from JSON file"""
    temp_dir = None
    print("Importing JSON data")
    try:
        # Log the incoming file
        logger.info(f"Receiving JSON file: {file.filename}")
        
        # Save uploaded JSON temporarily
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        
        # Log the temp path
        logger.info(f"Saving to temporary path: {temp_path}")
        
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Log before import
        logger.info("Starting JSON import...")
        
        # Import the data
        result = db.import_from_json(temp_path)
        
        # Log success
        logger.info(f"Import successful: {result}")
        return result
        
    except Exception as e:
        # Log the error
        logger.error(f"Error during JSON import: {str(e)}")
        # Ensure session is rolled back
        if hasattr(db, 'session'):
            db.session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Cleanup temp files
        if temp_dir:
            try:
                os.remove(os.path.join(temp_dir, file.filename))
                os.rmdir(temp_dir)
                logger.info("Temporary files cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up temp files: {str(e)}")

@app.post("/debug/reset-db")
async def reset_database():
    """Reset the database by dropping all tables and recreating them"""
    try:
        logger.info("Dropping all tables...")
        Base.metadata.drop_all(db_session.engine)
        logger.info("Recreating all tables...")
        Base.metadata.create_all(db_session.engine)
        return {"message": "Database reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/table-info")
async def get_table_info():
    """Get information about the database tables"""
    try:
        inspector = inspect(db_session.engine)
        tables = {}
        for table_name in inspector.get_table_names():
            columns = []
            for column in inspector.get_columns(table_name):
                columns.append({
                    "name": column["name"],
                    "type": str(column["type"])
                })
            tables[table_name] = columns
        return {"tables": tables}
    except Exception as e:
        logger.error(f"Error getting table info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
