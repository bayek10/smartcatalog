import React, { useState } from 'react';
import './SearchForm.css';
import './ProductTable.css';
import { API_URL, STORAGE_URL } from '../config';
import { Tabs } from './Tabs';

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

// Define the type for the elements of boqResults
type BoqResult = {
    boqItem: any;
    matches: Product[];
    selectedMatch?: Product;
};

export const SearchForm = () => {
    const [query, setQuery] = useState('');
    const [processedData, setProcessedData] = useState([]);
    const [file, setFile] = useState<File | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [activeTab, setActiveTab] = useState('upload');
    const [boqFile, setBoqFile] = useState<File | null>(null);
    const [boqResults, setBoqResults] = useState<Array<{
        boqItem: any;
        matches: Product[];
        selectedMatch?: Product;
    }>>([]);
    const [isProcessingBoq, setIsProcessingBoq] = useState(false);
    const [boqText, setBoqText] = useState<string>('');

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const response = await fetch(`${API_URL}/search?query=${encodeURIComponent(query)}`);
            if (!response.ok) {
                throw new Error('Search failed');
            }
            const data = await response.json();
            setProcessedData(data);
            if (data.length === 0) {
                alert('No products found');
            }
        } catch (error) {
            console.error('Search error:', error);
            alert('Error performing search');
        }
    };

    const handleFileUpload = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!file) {
            alert('Please select a file first');
            return;
        }

        setIsUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_URL}/upload`, {
                method: 'POST',
                body: formData,
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Upload failed');
            }
            
            const result = await response.json();
            alert(result.message);
            // Refresh the product list after upload
            handleViewProcessedData();
        } catch (error) {
            console.error('Upload error details:', error);
            alert(`Error uploading PDF: ${error instanceof Error ? error.message : 'Unknown error'}`);
        } finally {
            setIsUploading(false);
            setFile(null);
        }
    };

    const handleViewProcessedData = async () => {
        const response = await fetch(`${API_URL}/debug/products`);
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

            const response = await fetch(`${API_URL}/import-json`, {
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
        } catch (error: unknown) {
            console.error('Upload error:', error);
            if (error instanceof Error) {
                alert(`Error uploading JSON: ${error.message}`);
            } else {
                alert('Error uploading JSON');
            }
        }
    };

    const handleDeleteAllData = async () => {
        try {
            const response = await fetch(`${API_URL}/debug/products`, {
                method: 'DELETE',
            });
            
            if (response.ok) {
                // Clear the local state
                setProcessedData([]);
                alert('All products deleted successfully');
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to delete products');
            }
        } catch (error: unknown) {
            if (error instanceof Error) {
                alert(`Error deleting products: ${error.message}`);
            } else {
                alert('Error deleting products');
            }
        }
    };

    const renderColorsList = (colors: string[]) => {
        if (!colors || colors.length === 0) return '-';
        const displayColors = colors.slice(0, 3);
        return displayColors.join(', ') + (colors.length > 3 ? ` +${colors.length - 3} more` : '');
    };

    const getPdfLink = (pageRef: { file_path: string; page_numbers: number[] }) => {
        if (!pageRef || !pageRef.page_numbers || pageRef.page_numbers.length === 0) return '#';
        
        const fileName = pageRef.file_path;
        return `${STORAGE_URL}/${fileName}#page=${pageRef.page_numbers[0]}`;
    };

    const handleBoqUpload = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!boqFile) {
            alert('Please select a BOQ file first');
            return;
        }

        setIsProcessingBoq(true);
        const formData = new FormData();
        formData.append('file', boqFile);

        try {
            const response = await fetch(`${API_URL}/process-boq`, {
                method: 'POST',
                body: formData,
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'BOQ processing failed');
            }
            
            const results = await response.json();
            setBoqResults(results);
        } catch (error) {
            console.error('BOQ processing error:', error);
            alert(`Error processing BOQ: ${error instanceof Error ? error.message : 'Unknown error'}`);
        } finally {
            setIsProcessingBoq(false);
            setBoqFile(null);
        }
    };

    const handleBoqTextProcess = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!boqText.trim()) {
            alert('Please enter some products to match');
            return;
        }

        setIsProcessingBoq(true);
        try {
            // Convert text input to structured data
            const items = boqText.split('\n')
                .map(line => line.trim())
                .filter(line => line.length > 0)
                .map(line => {
                    const [name, brand, type] = line.split(',').map(s => s.trim());
                    if (!name || !brand || !type) {
                        throw new Error('Each line must contain product name, brand name, and product type separated by commas');
                    }
                    return { name, brand, type };
                });

            const response = await fetch(`${API_URL}/process-boq-text`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ items }),
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'BOQ processing failed');
            }
            
            const results = await response.json();
            setBoqResults(results);
            
            if (results.some((result: BoqResult) => result.matches.length === 0)) {
                alert('Some items had no matches. Please check the results carefully.');
            }
        } catch (error) {
            console.error('BOQ processing error:', error);
            alert(`Error processing BOQ: ${error instanceof Error ? error.message : 'Unknown error'}`);
        } finally {
            setIsProcessingBoq(false);
        }
    };

    const renderUploadTab = () => (
        <>
            <div className="instructions-panel">
                <h2>How it works</h2>
                <ol className="steps-list">
                    <li>Upload your catalog or price list (in PDF form) using the form below</li>
                    <li>Wait for the system to process your document</li>
                    <li>Switch to the Product List tab to explore your catalog</li>
                </ol>
            </div>

            <div className="upload-section">
                <h2>Upload Your Catalog</h2>
                <div className="upload-options">
                    <div className="upload-option">
                        <h3>PDF Upload</h3>
                        <p className="helper-text">Upload your product catalog in PDF format</p>
                        <form onSubmit={handleFileUpload} className="upload-form">
                            <input 
                                type="file"
                                accept=".pdf"
                                onChange={(e) => setFile(e.target.files?.[0] || null)}
                                className="file-input"
                            />
                            <button 
                                type="submit" 
                                className="primary-button" 
                                disabled={isUploading}
                            >
                                {isUploading ? 'Processing...' : 'Process Catalog'}
                            </button>
                        </form>
                    </div>

                    <div className="upload-option">
                        <h3>JSON Import</h3>
                        <p className="helper-text">Already have product data? Import it directly</p>
                        <form onSubmit={handleJsonUpload} className="upload-form">
                            <input 
                                type="file"
                                accept=".json"
                                onChange={(e) => setFile(e.target.files?.[0] || null)}
                                className="file-input"
                            />
                            <button type="submit" className="primary-button">Import Data</button>
                        </form>
                    </div>
                </div>
            </div>
        </>
    );

    const renderSearchTab = () => (
        <>
            <div className="search-section">
                <h2>Search Your Products</h2>
                <p className="helper-text">Search by product name, brand, designer, or any other detail</p>
                <form onSubmit={handleSearch} className="search-form">
                    <input 
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Type to search products..."
                        className="search-input"
                    />
                    <button type="submit" className="primary-button">Search</button>
                </form>
                
                <div className="view-options">
                    <button 
                        onClick={handleViewProcessedData} 
                        className="secondary-button"
                    >
                        View All Products
                    </button>
                    <button     
                        onClick={handleDeleteAllData} 
                        className="danger-button"
                        title="Remove all products from the catalog"
                    >
                        Clear Catalog
                    </button>
                </div>
            </div>
            
            <div className="processed-section">
                {processedData.length > 0 && (
                    <div className="table-container">
                        <h2>Product Catalog</h2>
                        <div className="table-header">
                            <p className="product-count">
                                {processedData.length} product{processedData.length !== 1 ? 's' : ''} found
                            </p>
                        </div>
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
                                                    View Page
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
        </>
    );

    const renderBoqTab = () => (
        <>
            <div className="instructions-panel">
                <h2>Match BOQ Items</h2>
                <ol className="steps-list">
                    <li>Upload a BOQ file or enter products manually below</li>
                    <li>The system will match each item to products in the database</li>
                    <li>Review matches and find pricing in the referenced catalogs</li>
                </ol>
            </div>

            <div className="boq-input-options">
                <div className="boq-input-option disabled">
                    <div className="coming-soon-overlay">
                        <span>Coming Soon</span>
                    </div>
                    <h3>Upload BOQ File</h3>
                    <p className="helper-text">Upload your Bill of Quantities file (as Excel, CSV, or JSON file)</p>
                    <form onSubmit={handleBoqUpload} className="upload-form">
                        <input 
                            type="file"
                            accept=".xlsx,.xls,.csv,.json"
                            onChange={(e) => setBoqFile(e.target.files?.[0] || null)}
                            className="file-input"
                            disabled
                        />
                        <button 
                            type="submit" 
                            className="primary-button" 
                            // disabled={isProcessingBoq}
                            disabled
                        >
                            {/* {isProcessingBoq ? 'Processing...' : 'Process BOQ'} */}
                            Process BOQ
                        </button>
                    </form>
                </div>

                <div className="boq-input-option">
                    <h3>Enter Products Manually</h3>
                    <p className="helper-text">
                        Enter one product per line in the format:<br/>
                        <code>product name, brand name, product type</code>
                    </p>
                    <form onSubmit={handleBoqTextProcess} className="text-input-form">
                        <textarea
                            value={boqText}
                            onChange={(e) => setBoqText(e.target.value)}
                            placeholder="Example:
Butterfly Keramik, Cattelan Italia, tavolo
Pattie, Minotti, poltrona"
                            className="boq-text-input"
                            rows={6}
                        />
                        <button 
                            type="submit" 
                            className="primary-button"
                            disabled={isProcessingBoq}
                        >
                            {isProcessingBoq ? 'Processing...' : 'Process Items'}
                        </button>
                    </form>
                </div>
            </div>

            {boqResults.length > 0 && (
                <div className="boq-results">
                    <h2>BOQ Matching Results</h2>
                    <table className="product-table">
                        <thead>
                            <tr>
                                <th>BOQ Item</th>
                                <th>Matched Product</th>
                                <th>Reference Page</th>
                            </tr>
                        </thead>
                        <tbody>
                            {boqResults.map((result, index) => (
                                <tr key={index}>
                                    <td>
                                        <div className="boq-item-details">
                                            <strong>{result.boqItem.name}</strong>
                                            <small>
                                                {result.boqItem.brand && `Brand: ${result.boqItem.brand}`}<br/>
                                                {result.boqItem.type && `Type: ${result.boqItem.type}`}
                                            </small>
                                        </div>
                                    </td>
                                    <td>
                                        {result.matches.length > 0 ? (
                                            <select 
                                                value={result.selectedMatch?.id || ''}
                                                onChange={(e) => {
                                                    const match = result.matches.find(m => m.id === Number(e.target.value));
                                                    const newResults = [...boqResults];
                                                    newResults[index].selectedMatch = match;
                                                    setBoqResults(newResults);
                                                }}
                                            >
                                                {result.matches.map(match => (
                                                    <option key={match.id} value={match.id}>
                                                        {match.product_name} ({match.brand_name})
                                                    </option>
                                                ))}
                                            </select>
                                        ) : (
                                            <span className="no-matches">No matches found</span>
                                        )}
                                    </td>
                                    <td>
                                        {result.selectedMatch?.page_reference && (
                                            <a 
                                                href={getPdfLink(result.selectedMatch.page_reference)}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="view-catalog-link"
                                            >
                                                View in Catalog
                                            </a>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </>
    );

    return (
        <div className="container">
            <Tabs activeTab={activeTab} onTabChange={setActiveTab} />
            
            {activeTab === 'upload' && renderUploadTab()}
            {activeTab === 'search' && renderSearchTab()}
            {activeTab === 'boq' && renderBoqTab()}
        </div>
    );
}; 