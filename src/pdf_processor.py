import pdfplumber
import re
from typing import Dict, List, Optional

class PDFProcessor:
    # Added Italian furniture types
    FURNITURE_TYPES = [
        # Italian terms
        'divano', 'sedia', 'tavolo', 'letto', 'armadio', 'cassettiera', 'scrivania',
        'libreria', 'guardaroba', 'poltrona', 'pouf', 'panca', 'sgabello',
        'credenza', 'consolle', 'comodino', 'scaffale', 'vetrina',
        # Include English terms as fallback
        'sofa', 'chair', 'table', 'bed', 'cabinet', 'dresser', 'desk',
        'bookshelf', 'wardrobe', 'armchair', 'ottoman', 'bench', 'stool'
    ]

    # Italian dimension indicators
    DIMENSION_INDICATORS = ['lunghezza', 'larghezza', 'altezza', 'profondità', 'diametro',
                          'lung', 'larg', 'alt', 'prof', 'diam', 'ø']

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        
    def extract_product_info(self):
        products = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Extract text
                text = page.extract_text()
                
                # Process and structure the data
                product_data = self._parse_page_content(text)
                
                if product_data:
                    product_data['page_number'] = page_num + 1
                    product_data['source_pdf'] = self.pdf_path
                    products.append(product_data)
                
        return products
    
    def _parse_page_content(self, text):
        # Basic implementation for testing
        return {
            'id': len(text),  # temporary unique id
            'name': 'Test Product',
            'price': '99.99',
            'dimensions': '10x10',
            'text_content': text[:100] if text else ''  # first 100 chars of text
        }

    def _parse_product_block(self, text: str) -> Optional[Dict]:
        product_data = {}
        
        # Brand detection remains similar as brands are usually in caps
        brand_match = re.search(r'^([A-Z][A-Z\s]+)(?:\s|$)', text, re.MULTILINE)
        if brand_match:
            product_data['brand'] = brand_match.group(1).strip()
        
        # Product type detection in Italian
        text_lower = text.lower()
        for furniture_type in self.FURNITURE_TYPES:
            if furniture_type in text_lower:
                product_data['type'] = furniture_type
                break
        
        # Modified dimension pattern to match Italian formats
        # Examples: "L.160 x P.90 x H.75 cm" or "160x90x75 cm" or "Ø120 cm"
        dim_patterns = [
            r'(?:L\.?|lung\.?)?\s*(\d+(?:[,.]\d+)?)\s*(?:x|×)\s*(?:P\.?|prof\.?)?\s*(\d+(?:[,.]\d+)?)\s*(?:x|×)\s*(?:H\.?|alt\.?)?\s*(\d+(?:[,.]\d+)?)\s*(?:cm|mm)?',
            r'Ø\s*(\d+(?:[,.]\d+)?)\s*(?:cm|mm)?',  # For circular items
            r'(?:diam\.?|diametro)\s*(\d+(?:[,.]\d+)?)\s*(?:cm|mm)?'  # Alternative diameter format
        ]
        
        for pattern in dim_patterns:
            dim_match = re.search(pattern, text, re.IGNORECASE)
            if dim_match:
                if len(dim_match.groups()) == 3:  # LxPxH format
                    dims = [dim_match.group(1), dim_match.group(2), dim_match.group(3)]
                    product_data['dimensions'] = 'x'.join(dims)
                else:  # Diameter format
                    product_data['dimensions'] = f"Ø{dim_match.group(1)}"
                break

        # Price pattern adjusted for Euro format (1.234,56 €)
        def _clean_price(price_str: str) -> Optional[float]:
            try:
                # Remove currency symbol and spaces
                price_str = price_str.replace('€', '').replace(' ', '')
                # Convert from European format (1.234,56) to standard float format (1234.56)
                price_str = price_str.replace('.', '').replace(',', '.')
                return float(price_str)
            except ValueError:
                return None

    def _find_price_in_tables(self, tables: List[List[List[str]]], product_name: Optional[str]) -> Optional[float]:
        if not product_name or not tables:
            return None
            
        for table in tables:
            for row in table:
                row_text = ' '.join(str(cell).lower() for cell in row if cell)
                if product_name.lower() in row_text:
                    # Modified price pattern for Euro format
                    price_match = re.search(r'(\d+(?:\.?\d{3})*(?:,\d{2})?)\s*€', row_text)
                    if price_match:
                        price_str = price_match.group(1)
                        return self._clean_price(price_str)
        return None