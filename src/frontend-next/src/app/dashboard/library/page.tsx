'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import { API_URL, STORAGE_URL } from '@/lib/config'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { ProductFilters } from "@/components/ui/product-filters"
import { Separator } from "@/components/ui/separator"
import { Product, FilterState } from '@/types'

export default function LibraryPage() {
  const [query, setQuery] = useState('')
  const [products, setProducts] = useState<Product[]>([])
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([])
  const { toast } = useToast()

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const searchParams = new URLSearchParams()
      if (query) searchParams.append('query', query)
      
      const response = await fetch(`${API_URL}/search?${searchParams}`)
      if (!response.ok) throw new Error('Search failed')
      const data = await response.json()
      setProducts(data)
      if (data.length === 0) {
        toast({
          title: "No results",
          description: "No products found matching your search",
        })
      }
    } catch (error) {
      console.error('Search error:', error)
      toast({
        title: "Error",
        description: "Failed to search products",
        variant: "destructive"
      })
    }
  }

  const handleViewAll = async () => {
    try {
      const searchParams = new URLSearchParams()
      
      const response = await fetch(`${API_URL}/debug/products?${searchParams}`)
      const data = await response.json()
      setProducts(data.products)
    } catch (error) {
      console.error('View all error:', error)
      toast({
        title: "Error",
        description: "Failed to load products",
        variant: "destructive"
      })
    }
  }

  const handleClearCatalog = async () => {
    try {
      const response = await fetch(`${API_URL}/debug/products`, {
        method: 'DELETE',
      })
      if (!response.ok) throw new Error('Failed to clear catalog')
      setProducts([])
      toast({
        title: "Success",
        description: "Catalog cleared successfully",
      })
    } catch (error) {
        console.error('Clear catalog error:', error)
        toast({
        title: "Error",
        description: "Failed to clear catalog",
        variant: "destructive"
      })
    }
  }

  const handleFilterApply = (filters: FilterState) => {
    let filtered = [...products]

    // Apply each filter
    if (filters.brand_names.length > 0) {
      filtered = filtered.filter(p => filters.brand_names.includes(p.brand_name))
    }
    if (filters.designers.length > 0) {
      filtered = filtered.filter(p => filters.designers.includes(p.designer))
    }
    if (filters.types.length > 0) {
      filtered = filtered.filter(p => filters.types.includes(p.type_of_product))
    }
    if (filters.colors.length > 0) {
      filtered = filtered.filter(p => 
        p.all_colors?.some(color => filters.colors.includes(color))
      )
    }
    if (filters.pdfs.length > 0) {
      filtered = filtered.filter(p => 
        filters.pdfs.includes(p.page_reference?.file_path)
      )
    }

    setFilteredProducts(filtered)
  }

  const renderColorsList = (colors: string[]) => {
    if (!colors?.length) return '-'
    const displayColors = colors.slice(0, 3)
    return displayColors.join(', ') + (colors.length > 3 ? ` +${colors.length - 3} more` : '')
  }

  const getPdfLink = (pageRef: { file_path: string; page_numbers: number[] }) => {
    if (!pageRef?.page_numbers?.length) return '#'
    return `${STORAGE_URL}/${pageRef.file_path}#page=${pageRef.page_numbers[0]}`
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Product Library</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Search Section */}
          <form onSubmit={handleSearch} className="flex gap-4 mb-6">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search products..."
              className="flex-1"
            />
            <Button type="submit">Search</Button>
          </form>

          {/* Primary Actions */}
          <div className="flex gap-2 mb-6">
            <Button variant="outline" onClick={handleViewAll}>
              View All Products
            </Button>
            <Button variant="destructive" onClick={handleClearCatalog}>
              Clear Catalog
            </Button>
          </div>

          <Separator className="my-4" />

          {products.length > 0 && (
            <>
              {/* Filter Section */}
              <div className="rounded-lg bg-muted/50 p-4 space-y-4">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-medium">Filters</h3>
                    <span className="text-sm text-muted-foreground">({filteredProducts.length} items)</span>
                  </div>
                </div>
                <ProductFilters 
                  products={products} 
                  onFilterApply={handleFilterApply} 
                />
              </div>
              {/* Results Table */}
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Product Name</TableHead>
                      <TableHead>Brand</TableHead>
                      <TableHead>Designer</TableHead>
                      <TableHead>Year</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Colors</TableHead>
                      <TableHead>PDF Page</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredProducts.length > 0 ? (
                      filteredProducts.map((product) => (
                        <TableRow key={product.id}>
                          <TableCell>{product.product_name || '-'}</TableCell>
                          <TableCell>{product.brand_name || '-'}</TableCell>
                          <TableCell>{product.designer || '-'}</TableCell>
                          <TableCell>{product.year || '-'}</TableCell>
                          <TableCell>{product.type_of_product || '-'}</TableCell>
                          <TableCell title={product.all_colors?.join(', ')}>
                            {renderColorsList(product.all_colors)}
                          </TableCell>
                          <TableCell>
                            {product.page_reference && (
                              <Button
                                variant="link"
                                asChild
                              >
                                <a
                                  href={getPdfLink(product.page_reference)}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                >
                                  View Page
                                </a>
                              </Button>
                            )}
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={7} className="text-center py-4 text-muted-foreground">
                          No products match the selected filters
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
