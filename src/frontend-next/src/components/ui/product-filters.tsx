'use client'

import { useState } from 'react'
import { Check, ChevronsUpDown } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandDialog,
  CommandList,
} from "@/components/ui/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Product, FilterState } from '@/types'

interface ProductFiltersProps {
  products: Product[]
  onFilterApply: (filters: FilterState) => void
}

export function ProductFilters({ products, onFilterApply }: ProductFiltersProps) {
  const [filters, setFilters] = useState<FilterState>({
    brand_names: [],
    designers: [],
    types: [],
    colors: [],
    pdfs: []
  })
  const [open, setOpen] = useState<{ [key: string]: boolean }>({})

  // Extract unique values for each filter
  const uniqueValues = {
    brand_names: [...new Set(products.map(p => p.brand_name).filter(Boolean))].sort(),
    designers: [...new Set(products.map(p => p.designer).filter(Boolean))].sort(),
    types: [...new Set(products.map(p => p.type_of_product).filter(Boolean))].sort(),
    colors: [...new Set(products.flatMap(p => p.all_colors || []))].sort(),
    pdfs: [...new Set(products.map(p => p.page_reference?.file_path).filter(Boolean))].sort()
  }

  const handleFilterChange = (filterType: keyof FilterState, value: string) => {
    setFilters(prev => {
      const newFilters = { ...prev }
      if (newFilters[filterType].includes(value)) {
        newFilters[filterType] = newFilters[filterType].filter(v => v !== value)
      } else {
        newFilters[filterType] = [...newFilters[filterType], value]
      }
      return newFilters
    })
  }

  const handleApplyFilters = () => {
    onFilterApply(filters)
  }

  const handleClearFilters = () => {
    setFilters({
      brand_names: [],
      designers: [],
      types: [],
      colors: [],
      pdfs: []
    })
    onFilterApply({
      brand_names: [],
      designers: [],
      types: [],
      colors: [],
      pdfs: []
    })
  }

  const renderCombobox = (filterType: keyof FilterState, label: string) => (
    <Popover open={open[filterType]} onOpenChange={(isOpen) => setOpen(prev => ({ ...prev, [filterType]: isOpen }))}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          className="w-[200px] justify-between"
        >
          {filters[filterType].length > 0 
            ? `${label} (${filters[filterType].length})`
            : label}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0">
        <Command>
          <CommandInput placeholder={`Search ${label.toLowerCase()}...`} />
          <CommandList>
            <CommandEmpty>No {label.toLowerCase()} found.</CommandEmpty>
            <CommandGroup>
              <ScrollArea className="h-[200px]">
                {uniqueValues[filterType].map((item) => (
                  <CommandItem
                    key={item}
                    value={item}
                    onSelect={() => handleFilterChange(filterType, item)}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        filters[filterType]?.includes(item) ? "opacity-100" : "opacity-0"
                      )}
                    />
                    {filterType === 'pdfs' ? item.split('/').pop() : item}
                  </CommandItem>
                ))}
              </ScrollArea>
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-4">
        {renderCombobox('brand_names', 'Brand')}
        {renderCombobox('designers', 'Designer')}
        {renderCombobox('types', 'Product Type')}
        {renderCombobox('colors', 'Color')}
        {renderCombobox('pdfs', 'PDF Source')}
      </div>

      <div className="flex gap-2">
        <Button 
          variant="secondary" 
          onClick={handleApplyFilters}
          className="bg-primary/10 hover:bg-primary/20"
        >
          Apply Filters
        </Button>
        <Button 
          variant="ghost" 
          onClick={handleClearFilters}
          size="sm"
        >
          Clear
        </Button>
      </div>
    </div>
  )
}