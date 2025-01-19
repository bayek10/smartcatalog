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

export default function LibraryPage() {
  const [query, setQuery] = useState('')
  const [products, setProducts] = useState<Product[]>([])
  const { toast } = useToast()

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await fetch(`${API_URL}/search?query=${encodeURIComponent(query)}`)
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
      toast({
        title: "Error",
        description: "Failed to search products",
        variant: "destructive"
      })
    }
  }

  const handleViewAll = async () => {
    try {
      const response = await fetch(`${API_URL}/debug/products`)
      const data = await response.json()
      setProducts(data.products)
    } catch (error) {
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
      toast({
        title: "Error",
        description: "Failed to clear catalog",
        variant: "destructive"
      })
    }
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
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Product Library</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="flex gap-4 mb-6">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search products..."
              className="flex-1"
            />
            <Button type="submit">Search</Button>
          </form>

          <div className="flex gap-2 mb-6">
            <Button variant="outline" onClick={handleViewAll}>
              View All Products
            </Button>
            <Button variant="destructive" onClick={handleClearCatalog}>
              Clear Catalog
            </Button>
          </div>

          {products.length > 0 && (
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
                  {products.map((product) => (
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
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
