from pdf_processor import PDFProcessor
from boq_processor import BoQProcessor
from dotenv import load_dotenv
import os
import json
import code
from pprint import pprint

test_processed_products = [{'product_name': 'ATLANTIS CRYSTALART', 'brand_name': 'Cattelan Italia', 'designer': 'Paolo Cattelan', 'year': 2019, 'type_of_product': 'Tavolo', 'all_colors': ['CY01', 'CY02', 'GFM11', 'GFM18', 'GFM69', 'GFM73'], 'page_reference': {'file_path': '..\\pdfs\\Cattelan Italia ITALIA 08.01.21-pages-2-11.pdf', 'page_numbers': [1], 'y_coord': 49.9630126953125}}, {'product_name': 'ATLANTIS KERAMIK', 'brand_name': 'Cattelan Italia', 'designer': 'Paolo Cattelan', 'year': 2019, 'type_of_product': 'Tavolo', 'all_colors': ['KM02', 'KM04', 'KM05', 'KM06', 'KM07', 'KM08', 'KM09', 'KM10', 'KM11', 'KM12', 'KM13', 'GFM11', 'GFM18', 'GFM69', 'GFM73'], 'page_reference': {'file_path': '..\\pdfs\\Cattelan Italia ITALIA 08.01.21-pages-2-11.pdf', 'page_numbers': [1], 'y_coord': 369.2239990234375}}, {'product_name': 'ATLANTIS WOOD', 'brand_name': 'Cattelan Italia', 'designer': 'Paolo Cattelan', 'year': 2019, 'type_of_product': 'Tavolo', 'all_colors': ['NC', 'HR', 'RB', 'RN', 'GFM11', 'GFM18', 'GFM69', 'GFM73'], 'page_reference': {'file_path': '..\\pdfs\\Cattelan Italia ITALIA 08.01.21-pages-2-11.pdf', 'page_numbers': [2], 'y_coord': 49.9630126953125}}, {'product_name': 'BORA BORA', 'brand_name': 'Cattelan Italia', 'designer': 'Giorgio Cattelan', 'year': '2014', 'type_of_product': 'Tavolo', 'all_colors': ['graphite', 'bianco', 'noce Canaletto', 'rovere bruciato'], 'page_reference': {'file_path': '..\\pdfs\\Cattelan Italia ITALIA 08.01.21-pages-2-11.pdf', 'page_numbers': ['3'], 'y_coord': 49.9630126953125}}, {'product_name': 'BUTTERFLY', 'brand_name': 'Cattelan Italia', 'designer': 'nucleo+', 'year': '2020', 'type_of_product': 'Tavolo', 'all_colors': ['titanio', 'bronzo', 'Brushed Bronze', 'Brushed Grey', 'cristallo trasparente', 'trasparente extrachiaro'], 'page_reference': {'file_path': '..\\pdfs\\Cattelan Italia ITALIA 08.01.21-pages-2-11.pdf', 'page_numbers': ['4'], 'y_coord': 49.9630126953125}}, {'product_name': 'BUTTERFLY KERAMIK', 'brand_name': 'Cattelan Italia', 'designer': 'nucleo+', 'year': 2020, 'type_of_product': 'Tavolo', 'all_colors': ['titanio', 'bronzo', 'Brushed Bronze', 'Brushed Grey', 'Alabastro', 'Ardesia', 'Golden Calacatta opaco', 'Golden Calacatta lucido', 'Portoro opaco', 'Portoro lucido', 'Sahara Noir lucido', 'Emperador', 'Makalu', 'Breccia', 'Arenal'], 'page_reference': {'file_path': '..\\pdfs\\Cattelan Italia ITALIA 08.01.21-pages-2-11.pdf', 'page_numbers': [5], 'y_coord': 49.9630126953125}}, {'product_name': 'CARIOCA', 'brand_name': 'Cattelan Italia', 'designer': 'Andrea Lucatello', 'year': 2014, 'type_of_product': 'Tavolo', 'all_colors': ['noce Canaletto', 'trasparente', 'extrachiaro'], 'page_reference': {'file_path': '..\\pdfs\\Cattelan Italia ITALIA 08.01.21-pages-2-11.pdf', 'page_numbers': [5], 'y_coord': 379.1759948730469}}, {'product_name': 'DAYTONA', 'brand_name': 'Cattelan Italia', 'designer': 'Studio Kronos', 'year': 2009, 'type_of_product': 'Tavolo allungabile', 'all_colors': ['acciaio inox lucido', 'noce Canaletto', 'cristallo temperato trasparente', 'extrachiaro trasparente'], 'page_reference': {'file_path': '..\\pdfs\\Cattelan Italia ITALIA 08.01.21-pages-2-11.pdf', 'page_numbers': [6], 'y_coord': 49.9630126953125}}, {'product_name': 'DIAPASON', 'brand_name': 'Cattelan Italia', 'designer': 'Studio Diapason', 'year': 1998, 'type_of_product': 'Tavolo', 'all_colors': ['Travertino', 'bianco Carrara', 'cristallo trasparente'], 'page_reference': {'file_path': '..\\pdfs\\Cattelan Italia ITALIA 08.01.21-pages-2-11.pdf', 'page_numbers': [6], 'y_coord': 518.6849975585938}}, {'product_name': 'DRAGON CRYSTALART', 'brand_name': 'Cattelan Italia', 'designer': 'Paolo Cattelan', 'year': 2019, 'type_of_product': 'Tavolo', 'all_colors': ['titanio (GFM11)', 'bronzo (GFM18)', 'graphite (GFM69)', 'nero (GFM73)', 'CY01', 'CY02'], 'page_reference': {'file_path': '..\\pdfs\\Cattelan Italia ITALIA 08.01.21-pages-2-11.pdf', 'page_numbers': [7], 'y_coord': 49.9630126953125}}, {'product_name': 'DRAGON KERAMIK', 'brand_name': 'Cattelan Italia', 'designer': 'Paolo Cattelan', 'year': 2019, 'type_of_product': 'Tavolo', 'all_colors': ['titanio (GFM11)', 'bronzo (GFM18)', 'graphite (GFM69)', 'nero (GFM73)', 'Alabastro (KM02)', 'Ardesia (KM04)', 'Golden Calacatta opaco (KM05)', 'Golden Calacatta lucido (KM06)', 'Portoro opaco (KM07)', 'Portoro lucido (KM08)', 'Sahara Noir lucido (KM09)', 'Emperador (KM10)', 'Makalu (KM11)', 'Breccia (KM12)', 'Arenal (KM13)'], 'page_reference': {'file_path': '..\\pdfs\\Cattelan Italia ITALIA 08.01.21-pages-2-11.pdf', 'page_numbers': [7], 'y_coord': 409.02099609375}}, {'product_name': 'DRAGON KERAMIK PREMIUM', 'brand_name': 'Cattelan Italia', 'designer': 'Paolo Cattelan', 'year': 2019, 'type_of_product': 'Tavolo', 'all_colors': ['titanio (GFM11)', 'bronzo (GFM18)', 'graphite (GFM69)', 'nero (GFM73)', 'Alabastro (KM02)', 'Ardesia (KM04)', 'Golden Calacatta opaco (KM05)', 'Golden Calacatta lucido (KM06)', 'Portoro opaco (KM07)', 'Portoro lucido (KM08)', 'Sahara Noir lucido (KM09)', 'Emperador (KM10)', 'Makalu (KM11)', 'Breccia (KM12)', 'Arenal (KM13)', 'Brushed Bronze', 'Brushed Grey'], 'page_reference': {'file_path': '..\\pdfs\\Cattelan Italia ITALIA 08.01.21-pages-2-11.pdf', 'page_numbers': [8], 'y_coord': 49.9630126953125}}, {'product_name': 'DRAGON WOOD', 'brand_name': 'Cattelan Italia', 'designer': 'Paolo Cattelan', 'year': 2019, 'type_of_product': None, 'all_colors': [], 'page_reference': {'file_path': '..\\pdfs\\Cattelan Italia ITALIA 08.01.21-pages-2-11.pdf', 'page_numbers': [8], 'y_coord': 410.6610107421875}}, {'product_name': 'HHH', 'brand_name': 'Cattelan Italia', 'designer': None, 'year': None, 'type_of_product': 'Tavolo', 'all_colors': ['titanio (GFM11)', 'bronzo (GFM18)', 'graphite (GFM69)', 'nero (GFM73)', 'noce Canaletto (NC)', 'rovere Heritage (HR)', 'rovere bruciato (RB)', 'rovere naturale (RN)', 'Brushed Grey', 'Olmo tinto poro aperto nero opaco (OLM73)', 'Brushed Bronze'], 'page_reference': {'file_path': '..\\pdfs\\Cattelan Italia ITALIA 08.01.21-pages-2-11.pdf', 'page_numbers': [9, 10], 'y_coord': 634.971435546875}}, {'product_name': 'DUFFY KERAMIK DRIVE', 'brand_name': 'Cattelan Italia', 'designer': 'Alberto Danese', 'year': 2018, 'type_of_product': 'Tavolo allungabile', 'all_colors': ['titanio (GFM11)', 'graphite (GFM69)', 'nero (GFM73)', 'Alabastro (KM02)', 'Ardesia (KM04)', 'Golden Calacatta opaco (KM05)', 'Golden Calacatta lucido (KM06)', 'Portoro opaco (KM07)', 'Portoro lucido (KM08)', 'Sahara Noir lucido (KM09)', 'Emperador (KM10)', 'Makalu (KM11)', 'Breccia (KM12)', 'Arenal (KM13)'], 'page_reference': {'file_path': '..\\pdfs\\Cattelan Italia ITALIA 08.01.21-pages-2-11.pdf', 'page_numbers': [10], 'y_coord': 442.4219970703125}}]

def test_processing():
    load_dotenv("api/.env")
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    pdf_path = "..\pdfs\Cattelan Italia ITALIA 08.01.21-pages-2-11.pdf"

    # 1. Process PDF and store results
    pdf_processor = PDFProcessor(pdf_path, GEMINI_API_KEY)
    processed_products = pdf_processor.extract_product_info()
    
    # 2. Process BoQ line using pre-processed data
    boq_processor = BoQProcessor("..\pdfs")
    result = boq_processor.process_boq_line(
        "Butterfly Keramik, Cattelan Italia, Table",
        processed_products
    )
    
    pprint(result, indent=2)
    code.interact(local=dict(globals(), **locals()))

if __name__ == "__main__":
    test_processing()

    