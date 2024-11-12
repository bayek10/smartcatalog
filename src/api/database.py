class ProductDB:
    def __init__(self):
        self.products = []  # For now, using in-memory storage. Later can switch to real DB
    
    def add_products(self, products):
        self.products.extend(products)
    
    def get_product(self, product_id):
        return next((p for p in self.products if p['id'] == product_id), None)
    
    def search(self, query, category=None, min_price=None, max_price=None):
        return self.products  # Basic implementation for now 