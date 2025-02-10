export interface Product {
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
}

export interface FilterState {
    brand_names: string[];
    designers: string[];
    types: string[];
    colors: string[];
    pdfs: string[];
}


