import fitz
from pathlib import Path
import google.generativeai as genai
import json
from typing import List, Dict, Optional, Tuple
import os
import logging
from dotenv import load_dotenv
import code

logger = logging.getLogger(__name__)

class BoQProcessor:
    def __init__(self, catalog_dir: str):
        self.catalog_dir = catalog_dir
        # self.gemini_api_key = gemini_api_key
        # self.processed_catalogs = {}  # Cache for processed PDFs
        # self.gemini_model = self._setup_gemini(gemini_api_key)
    
    # def _setup_gemini(self, api_key: str):
    #     """Initialize Gemini model"""
    #     genai.configure(api_key=api_key)
    #     return genai.GenerativeModel("gemini-1.5-pro-002")

            # STEP 1: Parse BoQ line
            # STEP 2: Find product in processed data & get y-coord
            # STEP 3: Find next product in processed data & get y-coord
            # STEP 4: Get all price tables within those bounds from the actual PDF

    def process_boq_line(self, boq_line: str, processed_products: List[Dict]) -> dict:
        """
        Main function to process a BoQ line and find product information.
        """
        try:
            # STEP 1: Parse BoQ line
            parsed_data = self._parse_boq_line(boq_line)
            
            # STEP 2: Find product in processed data & get y-coord
            # result = self._find_product_in_pdfs(parsed_data)
            # if result is None:
            #     return {
            #         "status": "not_found", 
            #         "message": f"Product {parsed_data['product_name']} not found in any catalog"
            #     }
            # pdf_name, page_num, page_text, prod_y_coord = result
            product = self._find_product(parsed_data, processed_products)
            if not product:
                return {
                    "status": "not_found",
                    "message": f"Product {parsed_data['product_name']} not found in database"
                }

            # STEP 3: Find next product in processed data & get y-coord
            next_product = self._find_next_product(product, processed_products)
            # if not next_product:
            #     return {
            #         "status": "not_found",
            #         "message": f"Next product for {parsed_data['product_name']} not found in database"
            #     }
            
            # STEP 4: Get all price tables within those bounds from the actual PDF
            # doc = fitz.open(Path(self.catalog_dir) / product["page_reference"]["file_path"])
            doc = fitz.open(product["page_reference"]["file_path"])
            try:
                price_tables = self._get_price_tables(doc, product, next_product)
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
                    "price_tables": price_tables
                }
            finally:
                doc.close()

            # try:
            #     # STEP 3: Extract product attributes
            #     all_products_structured = self._extract_product_attributes_gemini(
            #         page_text, pdf_name, page_num
            #     )
            #     product_attributes = all_products_structured[parsed_data["product_name"].upper()]
                
            #     ## STEP 4: find all price tables for our product
            #     # STEP 4A. Get y-coordinate range for product's section
            #     next_product_info = self._find_next_product_location(
            #         doc=doc,
            #         current_page=page_num,
            #         current_product=parsed_data["product_name"],
            #         products_on_page=all_products_structured
            #     )
                
            #     # STEP 4B. Get all price tables within those bounds
            #     price_tables = self._get_product_price_tables(
            #         doc=doc,
            #         start_page=page_num,
            #         end_page=next_product_info["page_num"] if next_product_info else None,
            #         start_y=prod_y_coord,
            #         end_y=next_product_info["y_coord"] if next_product_info else None
            #     )

            #     return {
            #         "status": "found",
            #         "product_info": {
            #             "name": parsed_data["product_name"],
            #             "brand": parsed_data["brand_name"],
            #             "type": parsed_data["product_type"],
            #             "designer": product_attributes["designer"],
            #             "year": product_attributes["year"],
            #             "catalog": pdf_name,
            #             "page": page_num
            #         },
            #         "specifications": parsed_data.get("specifications", {}),
            #         "available_options": {
            #             "colors": product_attributes["all_colors"],
            #         },
            #         "price_tables": price_tables,
            #         "section_bounds": {
            #             "start": {"page_num": page_num, "y_coord": prod_y_coord},
            #             "end": next_product_info if next_product_info else {
            #                 "page_num": len(doc), 
            #                 "y_coord": None
            #             }
            #         }
            #     }
            # finally:
            #     doc.close()

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

