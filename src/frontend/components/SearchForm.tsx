import React, { useState } from 'react';
import './SearchForm.css';
import './ProductTable.css';

type Product = {
    id: number;
    product_name: string;
    brand_name: string;
    designer: string;
    year: number;
    type_of_product: string;
    all_colors: string[];
    page_reference: {
        file_path: string;
        page_numbers: number[];
    };
};

export const SearchForm = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [file, setFile] = useState<File | null>(null);
    const [processedData, setProcessedData] = useState([]);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        const response = await fetch(`http://localhost:8080/search?query=${query}`);
        const data = await response.json();
        setResults(data);
    };

    const handleFileUpload = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('http://localhost:8080/upload', {
            method: 'POST',
            body: formData,
        });
        const result = await response.json();
        alert(result.message);
    };

    const handleViewProcessedData = async () => {
        const response = await fetch('http://localhost:8080/debug/products');
        const data = await response.json();
        setProcessedData(data.products);
    };

    const handleJsonUpload = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!file) {
            alert('Please select a file first');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('http://localhost:8080/import-json', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to import JSON');
            }

            const result = await response.json();
            alert(result.message || 'Successfully imported JSON data');
            
            // Clear the file input
            setFile(null);
            // Refresh the processed data view
            handleViewProcessedData();
        } catch (error) {
            console.error('Upload error:', error);
            alert(`Error uploading JSON: ${error.message}`);
        }
    };

    const handleDeleteAllData = async () => {
        try {
            const response = await fetch('http://localhost:8080/debug/products', {
                method: 'DELETE',
            });
            
            if (response.ok) {
                // Clear the local state
                setProcessedData([]);
                setResults([]);
                alert('All products deleted successfully');
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to delete products');
            }
        } catch (error) {
            alert(`Error deleting products: ${error.message}`);
        }
    };

    const renderColorsList = (colors: string[]) => {
        if (!colors || colors.length === 0) return '-';
        const displayColors = colors.slice(0, 3);
        return displayColors.join(', ') + (colors.length > 3 ? ` +${colors.length - 3} more` : '');
    };

    const getPdfLink = (pageRef: { file_path: string; page_numbers: number[] }) => {
        if (!pageRef || !pageRef.page_numbers || pageRef.page_numbers.length === 0) return '#';
        
        // Extract just the filename from the full path
        const fileName = pageRef.file_path.split('/').pop() || '';
        
        return `http://localhost:8080/pdfs/${encodeURIComponent(fileName)}#page=${pageRef.page_numbers[0]}`;
    };

    return (
        <div className="container">
            <div className="upload-section">
                <h2>Upload PDF</h2>
                <form onSubmit={handleFileUpload} className="upload-form">
                    <input 
                        type="file"
                        accept=".pdf"
                        onChange={(e) => setFile(e.target.files?.[0] || null)}
                    />
                    <button type="submit" className="primary-button">Upload PDF</button>
                </form>

                <h2>Upload JSON</h2>
                <form onSubmit={handleJsonUpload} className="upload-form">
                    <input 
                        type="file"
                        accept=".json"
                        onChange={(e) => setFile(e.target.files?.[0] || null)}
                    />
                    <button type="submit" className="primary-button">Import JSON</button>
                </form>

                <div className="data-controls">
                    <button 
                        onClick={handleViewProcessedData} 
                        className="secondary-button"
                    >
                        View Products
                    </button>
                    <button 
                        onClick={handleDeleteAllData} 
                        className="danger-button"
                    >
                        Delete All Data
                    </button>
                </div>
            </div>

            <div className="search-section">
                <h2>Search Products</h2>
                <form onSubmit={handleSearch} className="search-form">
                    <input 
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search products..."
                        className="search-input"
                    />
                    <button type="submit" className="primary-button">Search</button>
                </form>
            </div>
            
            <div className="results-section">
                {results.length > 0 && (
                    <div className="results-container">
                        <h2>Search Results</h2>
                        <div className="results-grid">
                            {results.map(product => (
                                <div key={product.id} className="product-card">
                                    <h3>{product.name}</h3>
                                    <p><strong>Price:</strong> {product.price}</p>
                                    <p><strong>Dimensions:</strong> {product.dimensions}</p>
                                    <p className="source-info">
                                        PDF: {product.source_pdf} (Page {product.page_number})
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            <div className="processed-section">
                {processedData.length > 0 && (
                    <div className="table-container">
                        <h2>Product Catalog</h2>
                        <table className="product-table">
                            <thead>
                                <tr>
                                    <th>Product Name</th>
                                    <th>Brand</th>
                                    <th>Designer</th>
                                    <th>Year</th>
                                    <th>Type</th>
                                    <th>Colors</th>
                                    <th>PDF Page</th>
                                </tr>
                            </thead>
                            <tbody>
                                {processedData.map((product: Product) => (
                                    <tr key={product.id}>
                                        <td>{product.product_name || '-'}</td>
                                        <td>{product.brand_name || '-'}</td>
                                        <td>{product.designer || '-'}</td>
                                        <td>{product.year || '-'}</td>
                                        <td>{product.type_of_product || '-'}</td>
                                        <td title={product.all_colors?.join(', ')}>
                                            {renderColorsList(product.all_colors)}
                                        </td>
                                        <td>
                                            {product.page_reference && (
                                                <a 
                                                    href={getPdfLink(product.page_reference)}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                >
                                                    View PDF
                                                </a>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}; 