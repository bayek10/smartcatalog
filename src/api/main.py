from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from .database import ProductDB, db_session
from ..pdf_processor import PDFProcessor
import tempfile
import os

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
