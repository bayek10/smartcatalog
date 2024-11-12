import React, { useState } from 'react';
import './SearchForm.css';

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
                <button 
                    onClick={handleViewProcessedData} 
                    className="secondary-button"
                >
                    View Processed Data
                </button>
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
                    <div className="processed-container">
                        <h2>Processed Data</h2>
                        <div className="results-grid">
                            {processedData.map(product => (
                                <div key={product.id} className="product-card">
                                    <h3>{product.name}</h3>
                                    <p><strong>Price:</strong> {product.price}</p>
                                    <p><strong>Dimensions:</strong> {product.dimensions}</p>
                                    <p className="source-info">
                                        PDF: {product.source_pdf} (Page {product.page_number})
                                    </p>
                                    <p className="text-preview">
                                        <strong>Preview:</strong> {product.text_content}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}; 