from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect
from typing import Optional
from google.cloud import storage
from .database import ProductDB, db_session
from .models import Base
from .config import ALLOW_ORIGINS, BUCKET_NAME, GEMINI_API_KEY, STORAGE_TYPE, PDF_STORAGE_PATH
from ..pdf_processor import PDFProcessor
import tempfile
import os
import logging
import shutil

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
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Google Cloud Storage client
storage_client = None
bucket = None
if STORAGE_TYPE == 'cloud':
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
if STORAGE_TYPE == 'local':
    # Mount the PDF directory
    os.makedirs(PDF_STORAGE_PATH, exist_ok=True)
    app.mount("/pdfs", StaticFiles(directory=PDF_STORAGE_PATH), name="pdfs")

@app.get("/search")
async def search_products(
    query: str,
    category: Optional[str] = None
):
    """
    Search products by query string.
    Query matches against product name, brand name, designer, type, color, year
    Optionally filter by category/type.
    """
    try:
        logger.info(f"Searching for query: {query}")
        results = db.search(
            query=query,
            category=category
        )
        logger.info(f"Found {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Log the start of processing
        logger.info(f"Starting upload process for file: {file.filename}")
        
        # Save the uploaded file to temp location
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"File saved to temp location: {temp_path}")
        
        # Process PDF
        processor = PDFProcessor(temp_path, GEMINI_API_KEY)
        logger.info("Starting PDF processing")
        products = processor.extract_product_info()
        logger.info(f"Extracted {len(products)} products")
        
        if STORAGE_TYPE == 'local':
            # Move to local storage
            final_path = os.path.join(PDF_STORAGE_PATH, file.filename)
            logger.info(f"Moving file to: {final_path}")
            
            # Remove existing file if it exists
            if os.path.exists(final_path):
                logger.info(f"Removing existing file: {final_path}")
                os.remove(final_path)
            
            # Use shutil.copy2 instead of os.rename
            shutil.copy2(temp_path, final_path)
            logger.info("File moved successfully")
            
            # Update file paths in products
            for product in products:
                if product.get('page_reference'):
                    product['page_reference']['file_path'] = file.filename
        else:
            # Cloud storage logic...
            logger.info("Using cloud storage")
            blob = bucket.blob(f"pdfs/{file.filename}")
            blob.upload_from_filename(temp_path)
            # Update file paths in products
            for product in products:
                if product.get('page_reference'):
                    product['page_reference']['file_path'] = f"pdfs/{file.filename}"
        
        # Store in database
        logger.info("Storing products in database")
        db.add_products(products)
        
        return {"message": f"Processed {len(products)} products from {file.filename}"}
    
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup temp files
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
            logger.info("Cleaned up temporary files")
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {str(e)}")

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
