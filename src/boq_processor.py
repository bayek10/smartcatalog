import fitz
from pathlib import Path
import google.generativeai as genai
from .price_extractor import PriceExtractor
import json
from typing import List, Dict, Optional, Tuple
import os
import logging
from dotenv import load_dotenv
import tempfile
from PIL import Image
import code

logger = logging.getLogger(__name__)

class BoQProcessor:
    def __init__(self, catalog_dir: str):
        self.catalog_dir = catalog_dir

    def get_price_data(self, current_prod: Dict, next_prod: Optional[Dict]):
        """Extract price tables between current and next product"""
        # Only handle price table extraction
        # No need for product finding or BOQ parsing
        try:
            pdf_path = os.path.join(self.catalog_dir, current_prod["page_reference"]["file_path"])
            logger.info(f"Opening PDF at: {pdf_path}")
            doc = fitz.open(pdf_path)
            
            # STEP 4: Get all price tables within those bounds from the actual PDF
            try:
                # Get table coordinates
                price_tables = self._get_price_tables(doc, current_prod, next_prod if next_prod else None)
                print("\nPRICE TABLES:\n", price_tables)

                if not price_tables:
                    logger.warning(f"No price tables found for product {current_prod['product_name']}")
                    return None

                # Process each table and extract prices
                processed_tables = self._process_price_tables(doc, price_tables)
                print("\nPROCESSED TABLES:\n", len(processed_tables))

                return {
                    "status": "found",
                    "price_tables": processed_tables
                }
            finally:
                doc.close()
        except Exception as e:
            logger.error(f"Error extracting prices: {str(e)}")
            return None
        
    # USELESS FUNCTIONS ALL THE WAY TO _get_price_tables. DELETE THEM ALL
    def process_boq_line(self, boq_line: str, processed_products: List[Dict]) -> dict:
        """
        USELESS DELETE. Main function to process a BoQ line and find product information.
        """
        try:
            # STEP 1: Parse BoQ line
            parsed_data = self._parse_boq_line(boq_line)
            
            # STEP 2: Find product in processed data & get y-coord
            product = self._find_product(parsed_data, processed_products)
            if not product:
                return {
                    "status": "not_found",
                    "message": f"Product {parsed_data['product_name']} not found in database"
                }

            # STEP 3: Find next product in processed data & get y-coord
            next_product = self._find_next_product(product, processed_products)
            
            doc = fitz.open(product["page_reference"]["file_path"])
            
            # STEP 4: Get all price tables within those bounds from the actual PDF
            try:
                # Get table coordinates
                price_tables = self._get_price_tables(doc, product, next_product)
                print("\nPRICE TABLES:\n", price_tables)

                # Process each table and extract prices
                processed_tables = self._process_price_tables(doc, price_tables)
                print("\nPROCESSED TABLES:\n", len(processed_tables))

                return {
                    "status": "found",
                    "product_info": {
                        "name": product["product_name"],
                        "brand": product["brand_name"],
                        "type": product["type_of_product"],
                        "designer": product.get("designer"),
                        "year": product.get("year"),
                        "catalog": product["page_reference"]["file_path"],  # or store pdf_name in PDFProcessor output
                        "page": product["page_reference"]["page_numbers"][0]
                    },
                    "specifications": parsed_data.get("specifications", {}),
                    "available_options": {
                        "colors": product.get("all_colors", []),
                    },
                    "price_tables": processed_tables
                }
            finally:
                doc.close()
        except Exception as e:
            logger.error(f"Error processing BoQ line: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _parse_boq_line(self, boq_line: str) -> dict:
        """Parse a line from Bill of Quantities into structured data."""
        parts = [p.strip() for p in boq_line.split(',')]
        
        if len(parts) < 3:
            raise ValueError("BoQ line must include: product name, brand name, product type")
            
        result = {
            "product_name": parts[0],
            "brand_name": parts[1],
            "product_type": parts[2],
            "specifications": {}
        }
        
        # Parse additional specifications
        for part in parts[3:]:
            if ':' in part:
                key, value = map(str.strip, part.split(':', 1))
                result["specifications"][key.lower()] = value
                
        return result

    def _find_product(self, parsed_data: dict, processed_products: List[Dict]) -> Optional[Dict]:
        """Find exact product match in processed data"""
        for product in processed_products:
            if (product["product_name"].upper() == parsed_data["product_name"].upper() and
                product["brand_name"].upper() == parsed_data["brand_name"].upper()):
                return product
        return None
    
    def _find_next_product(self, current_product: Dict, processed_products: List[Dict]) -> Optional[Dict]:
        """Find the next product in sequence"""
        # Sort products by page and y-coordinate. COULD BE REDUNDANT SINCE ALREADY DONE BY LLM IN ORDER
        sorted_products = sorted(
            processed_products,
            key=lambda p: (int(p["page_reference"]["page_numbers"][0]), p["page_reference"]["y_coord"])
        )
        
        # Find current product's index
        try:
            current_idx = sorted_products.index(current_product)
            if current_idx + 1 < len(sorted_products):
                return sorted_products[current_idx + 1]
        except ValueError:
            pass
        return None
   
    def _get_price_tables(self, doc: fitz.Document, current_product: Dict, next_product: Optional[Dict]) -> List[dict]:
        """Get all price tables between current product and next product"""
        tables = []
        start_page = int(current_product["page_reference"]["page_numbers"][0])
        end_page = int(next_product["page_reference"]["page_numbers"][0]) if next_product else len(doc)-1
        start_y = current_product["page_reference"]["y_coord"]
        end_y = next_product["page_reference"]["y_coord"] if next_product else None
        
        for page_num in range(start_page, end_page + 1):
            page = doc[page_num-1]
            page_tables = page.find_tables()
            
            for table in page_tables:
                table_bbox = table.bbox
                
                # Check if table is within our y-coordinate range
                if page_num == start_page and table_bbox[1] < start_y:
                    continue
                if page_num == end_page and end_y and table_bbox[1] > end_y:
                    continue
                    
                tables.append({
                    "page_num": page_num,
                    "bbox": table_bbox,
                    "content": table
                })
        # code.interact(local=dict(globals(), **locals()))
        return tables

    def _process_price_tables(self, doc: fitz.Document, tables: List[dict]) -> List[dict]:
        """Process each price table and extract pricing data"""
        load_dotenv("api/.env")

        # Get the absolute path to few-shot-examples
        current_dir = os.path.dirname(os.path.abspath(__file__))  # Gets src/
        few_shot_dir = os.path.join(current_dir, "..", "few-shot-examples")  

        price_extractor = PriceExtractor(
            claude_api_key=os.getenv('ANTHROPIC_API_KEY'),
            few_shot_examples_dir=few_shot_dir
        )
        print("PRICE EXTRACTOR INITIALIZED: ", price_extractor)

        processed_tables = []

        for table in tables:
            temp_file = None
            try:
                # Extract table image
                temp_file = self._extract_table_image(
                    doc=doc,
                    page_num=table["page_num"],
                    bbox=table["bbox"]
                )
                
                # Extract prices using Claude
                price_data = price_extractor.extract_prices(temp_file)

                if price_data:
                    processed_tables.append({
                        "page_num": table["page_num"],
                        "bbox": table["bbox"],
                        "price_data": price_data
                    })
                                
            except Exception as e:
                logger.error(f"Error processing table: {str(e)}")
                continue
            finally:
                # Clean up temp file with error handling
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.close(os.open(temp_file, os.O_RDONLY))  # Ensure file is closed
                        os.unlink(temp_file)  # Delete the file
                    except Exception as e:
                        logger.warning(f"Could not delete temporary file {temp_file}: {str(e)}")
        
        return processed_tables
    
    def _extract_table_image(self, doc: fitz.Document, page_num: int, bbox: tuple) -> str:
        """Extract table region as high-quality image from PDF"""
        page = doc[page_num-1]
        
        # Add padding to bbox to ensure table borders are included
        padding = 5  # pixels
        x0, y0, x1, y1 = bbox
        padded_bbox = fitz.Rect(x0 - padding, y0 - padding, 
                               x1 + padding, y1 + padding)

        # Get the pixmap of the table region
        zoom = 4  # Increased from 2 to 4 for higher resolution
        matrix = fitz.Matrix(zoom, zoom)

        # Get the pixmap withOUT alpha channel (produces transparent background not good for Claude) for better quality
        pix = page.get_pixmap(matrix=matrix, clip=padded_bbox)
        
        # Create temp file path but don't open it
        temp_dir = os.path.abspath(tempfile.gettempdir())
        temp_path = os.path.join(temp_dir, f"table_image_{next(tempfile._get_candidate_names())}.png")
        
        # Let PyMuPDF create and write the file directly
        pix.save(temp_path)
        return temp_path
        
        # # Save to temporary file with absolute path
        # with tempfile.NamedTemporaryFile(delete=False, 
        #                                suffix='.png', 
        #                                dir=os.path.abspath(tempfile.gettempdir())) as tmp:
        #     pix.save(tmp.name)
        #     return os.path.abspath(tmp.name)  # Return full absolute path
        

if __name__ == "__main__":
    load_dotenv("api/.env")
    
    # Initialize processor
    processor = BoQProcessor(
        catalog_dir="../pdfs/",  # Update this path to your PDF directory
        gemini_api_key=os.getenv('GEMINI_API_KEY')
    )
    
    # Test processing a BoQ line
    boq_line = "mad max wood, Cattelan Italia, Tavolo"
    result = processor.process_boq_line(boq_line)
    
    # Print results
    print("\nProcessing Results:")
    print("==================")
    print(f"Status: {result['status']}")
    if result['status'] == 'found':
        print("\nProduct Info:")
        for key, value in result['product_info'].items():
            print(f"{key}: {value}")
        print("\nPrice Tables Found:", len(result['price_tables']))
    else:
        print("Message:", result['message'])

    code.interact(local=dict(globals(), **locals()))


## OLD FUNCTIONS: used when we were not doing the pre-processing of PDFs first before BoQ processing. Saved in case

    # def _find_product_in_pdfs(self, parsed_data: dict) -> Optional[Tuple[str, int, str, float]]:
    #     """Find a product in all PDF catalogs in the specified directory."""
    #     pdf_files = list(Path(self.catalog_dir).glob("*.pdf"))
    #     if not pdf_files:
    #         logger.warning(f"No PDF files found in {self.catalog_dir}")
    #         return None
            
    #     for pdf_path in pdf_files:
    #         try:
    #             doc = fitz.open(pdf_path)
                
    #             try:
    #                 for page_num in range(len(doc)):
    #                     page = doc[page_num]
    #                     text = page.get_text()
                        
    #                     # Try uppercase version first
    #                     instances = page.search_for(parsed_data['product_name'].upper())
    #                     if not instances:
    #                         instances = page.search_for(parsed_data['product_name'])

    #                     if instances:
    #                         y_coord = instances[0].y0
    #                         logger.info(f"Found in {pdf_path.name} on page {page_num + 1}")
    #                         return (pdf_path.name, page_num, text, y_coord)
    #             finally:
    #                 doc.close()
                    
    #         except Exception as e:
    #             logger.error(f"Error processing {pdf_path}: {str(e)}")
    #             continue
            
    #     logger.warning(f"Product '{parsed_data['product_name']}' not found in any catalog")
    #     return None

    # def _extract_product_attributes_gemini(self, page_text: str, pdf_name: str, page_num: int) -> dict:
    #     """Use Gemini to extract product attributes from page text."""
    #     prompt = f"""
    #     The following is text extracted from a page of a PDF furniture catalog. It contains information for 1 or more products that the company sells. 
    #     Extract each product on the page in the same language (Italian) and output the data as a JSON object.
    #     The JSON object contains key-value pairs to represent each product, where the key is the name of the product and the value is an object containing the attributes listed below for that product:

    #     ATTRIBUTES:
    #     - brand_name: name of the brand
    #     - designer: name of the designer
    #     - year: year of manufacture
    #     - type_of_product: type of product (e.g., sofa, table, etc.)
    #     - all_colors: an array of all colors mentioned for the product along with their codes
    #     - page_reference: an object containing the PDF file path as a string and the page numbers of the product as an array

    #     TEXT FROM PAGE {page_num}:
    #     "{page_text}"
    #     """

    #     try:
    #         response = self.gemini_model.generate_content(
    #             prompt,
    #             generation_config=genai.GenerationConfig(
    #                 response_mime_type="application/json",
    #             ),
    #         )
            
    #         if response:
    #             structured_output = response.candidates[0].content.parts[0].text.strip()
    #             return json.loads(structured_output)
    #         else:
    #             logger.warning(f"Failed to parse page {page_num}")
    #             return {}
                
    #     except Exception as e:
    #         logger.error(f"Error processing with Gemini: {str(e)}")
    #         return {}

    # def _find_next_product_location(self, doc: fitz.Document, current_page: int, 
    #                               current_product: str, products_on_page: dict) -> Optional[dict]:
    #     """Find the next product's location after current product."""
    #     product_names = list(products_on_page.keys())
        
    #     try:
    #         current_index = product_names.index(current_product.upper())
    #         if current_index + 1 < len(product_names):
    #             next_product = product_names[current_index + 1]
    #             instances = doc[current_page].search_for(next_product.upper())
    #             return {
    #                 "page_num": current_page,
    #                 "y_coord": instances[0].y0,
    #                 "product_name": next_product
    #             }
    #     except ValueError:
    #         logger.warning(f"Warning: {current_product} not found in products list")
        
    #     # Check next pages
    #     for page_num in range(current_page + 1, len(doc)):
    #         try:
    #             page = doc[page_num]
    #             next_product = self._find_first_prod_on_page_gemini(page.get_text())
                
    #             if next_product:
    #                 instances = page.search_for(next_product.upper())
    #                 if instances:
    #                     return {
    #                         "page_num": page_num,
    #                         "y_coord": instances[0].y0,
    #                         "product_name": next_product
    #                     }
    #         except Exception as e:
    #             logger.error(f"Error processing page {page_num}: {str(e)}")
    #             continue

    #     return None

    # def _find_first_prod_on_page_gemini(self, page_text: str) -> Optional[str]:
    #     """Find first product name on a page if any exist"""
    #     prompt = f"""Analyze the furniture catalog page text below and identify if there are any product names. 
    #     Our goal is to determine if this page content contains new products or its just a continuation of the product on the last page. 
    #     Product names are typically in ALL CAPS and often followed by designer name and year.
    #     Return ONLY the first product name you find (in order of appearance) without saying anything else, or "NO_PRODUCT" if none found.

    #     Examples of output product names:
    #     - "BUTTERFLY KERAMIK"
    #     - "ATLANTIS CRYSTALART"
    #     - "SPYDER KERAMIK"

    #     <page_text>
    #     {page_text}
    #     </page_text>
    #     """
        
    #     try:
    #         response = self.gemini_model.generate_content(prompt)
    #         result = response.candidates[0].content.parts[0].text.strip()
            
    #         return None if result == "NO_PRODUCT" else result
            
    #     except Exception as e:
    #         logger.error(f"Error in Gemini API call: {str(e)}")
    #         return None
