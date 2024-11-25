import React from 'react';
import './Tabs.css';

type TabsProps = {
    activeTab: string;
    onTabChange: (tab: string) => void;
};

export const Tabs: React.FC<TabsProps> = ({ activeTab, onTabChange }) => {
    return (
        <div className="tabs">
            <button 
                className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
                onClick={() => onTabChange('upload')}
            >
                Upload Catalog
            </button>
            <button 
                className={`tab-button ${activeTab === 'search' ? 'active' : ''}`}
                onClick={() => onTabChange('search')}
            >
                Product List
            </button>
            <button 
                className={`tab-button ${activeTab === 'boq' ? 'active' : ''}`}
                onClick={() => onTabChange('boq')}
            >
                Process Bill of Quantities
            </button>
        </div>
    );
}; 