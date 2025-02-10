'use client'

import { useState } from 'react'
import type { GroupBase, Props } from 'react-select'
import ReactSelect from 'react-select'
import { Button } from "@/components/ui/button"
import { Product, FilterState } from '@/types'

interface ProductFiltersProps {
  products: Product[]
  onFilterApply: (filters: FilterState) => void
}

type Option = { label: string; value: string }

// Create a properly typed Select component
const Select = ReactSelect as unknown as <
  Option,
  IsMulti extends boolean = false,
  Group extends GroupBase<Option> = GroupBase<Option>
>(props: Props<Option, IsMulti, Group>) => JSX.Element

export function ProductFilters({ products, onFilterApply }: ProductFiltersProps) {
  const [filters, setFilters] = useState<FilterState>({
    brand_names: [],
    designers: [],
    types: [],
    colors: [],
    pdfs: []
  })

  // Extract unique values for each filter
  const uniqueValues = {
    brand_names: [...new Set(products.map(p => p.brand_name).filter(Boolean))].sort(),
    designers: [...new Set(products.map(p => p.designer).filter(Boolean))].sort(),
    types: [...new Set(products.map(p => p.type_of_product).filter(Boolean))].sort(),
    colors: [...new Set(products.flatMap(p => p.all_colors || []))].sort(),
    pdfs: [...new Set(products.map(p => p.page_reference?.file_path).filter(Boolean))].sort()
  }

  const handleFilterChange = (filterType: keyof FilterState, selected: readonly Option[]) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: selected.map(option => option.value)
    }))
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-4">
        <Select
          isMulti
          placeholder="Brand"
          options={uniqueValues.brand_names.map(b => ({ value: b, label: b }))}
          value={filters.brand_names.map(b => ({ value: b, label: b }))}
          onChange={(selected) => handleFilterChange('brand_names', selected as Option[])}
          className="w-[200px]"
        />
        <Select
          isMulti
          placeholder="Designer"
          options={uniqueValues.designers.map(d => ({ value: d, label: d }))}
          value={filters.designers.map(d => ({ value: d, label: d }))}
          onChange={(selected) => handleFilterChange('designers', selected as Option[])}
          className="w-[200px]"
        />
        <Select
          isMulti
          placeholder="Product Type"
          options={uniqueValues.types.map(t => ({ value: t, label: t }))}
          value={filters.types.map(t => ({ value: t, label: t }))}
          onChange={(selected) => handleFilterChange('types', selected as Option[])}
          className="w-[200px]"
        />
        <Select
          isMulti
          placeholder="Color"
          options={uniqueValues.colors.map(c => ({ value: c, label: c }))}
          value={filters.colors.map(c => ({ value: c, label: c }))}
          onChange={(selected) => handleFilterChange('colors', selected as Option[])}
          className="w-[200px]"
        />
        <Select
          isMulti
          placeholder="PDF Source"
          options={uniqueValues.pdfs.map(p => ({ 
            value: p, 
            label: p.split('/').pop() || p 
          }))}
          value={filters.pdfs.map(p => ({ 
            value: p, 
            label: p.split('/').pop() || p 
          }))}
          onChange={(selected) => handleFilterChange('pdfs', selected as Option[])}
          className="w-[200px]"
        />
      </div>

      <div className="flex gap-2">
        <Button 
          variant="secondary" 
          onClick={() => onFilterApply(filters)}
          className="bg-primary/10 hover:bg-primary/20"
        >
          Apply Filters
        </Button>
        <Button 
          variant="ghost" 
          onClick={() => {
            const emptyFilters = {
              brand_names: [],
              designers: [],
              types: [],
              colors: [],
              pdfs: []
            }
            setFilters(emptyFilters)
            onFilterApply(emptyFilters)
          }}
          size="sm"
        >
          Clear
        </Button>
      </div>
    </div>
  )
}