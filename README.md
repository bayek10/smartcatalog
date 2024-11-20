# Smart Catalog - Furniture Catalog Parser

Smart Catalog is a tool designed to extract and organize unstructured data from furniture catalog PDFs into structured, searchable products. This allows users to filter, search, and view catalog data efficiently, saving time and effort that would have been spent manually filtering through dozens of PDFs each containing hundreds of pages.

---

## Features
- **PDF Ingestion**: Upload furniture catalogs in PDF format.
- **Data Extraction**: Extract product details such as name, brand, type, colors, and more.
- **Semantic Structuring**: Use Google Gemini AI to transform unstructured text into structured JSON objects.
- **Searchable Results**: View and search structured data through a user-friendly interface.
- **Catalog Reference**: Includes page references to the original PDF for additional context & double-checking.

---

## Tech Stack
### **Backend**
- Python (FastAPI)
- Google Cloud Run for deployment
- PyMuPDF (`fitz`) for text extraction
- Google Gemini AI for semantic restructuring

### **Frontend**
- React
- Hosted on Firebase Hosting

### **Database**
- PostgreSQL hosted on Google Cloud SQL

### **Storage**
- Google Cloud Storage for storing uploaded PDFs

![Alt text](/src/frontend/public/smartcatalog-screenshot.png?raw=true "app screenshot")
