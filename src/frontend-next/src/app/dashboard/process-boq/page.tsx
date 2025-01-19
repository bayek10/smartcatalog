'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"


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
    price_data: Record<string, number | string | undefined> | null;
};


type BoqResult = {
  status: 'found' | 'not_found';
  boqItem: { name: string; brand: string; type: string };
  message?: string;
  matches: Product[];
  selectedMatch?: Product;
};

export default function BoqPage() {
  const [boqText, setBoqText] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [results, setResults] = useState<BoqResult[]>([])
  const { toast } = useToast()

  const handleProcessBoq = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!boqText.trim()) {
      toast({
        title: "Error",
        description: "Please enter some products to match",
        variant: "destructive"
      })
      return
    }

    setIsProcessing(true)
    try {
      const items = boqText.split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .map(line => {
          const [name, brand, type] = line.split(',').map(s => s.trim())
          if (!name || !brand || !type) {
            throw new Error('Each line must contain product name, brand name, and product type separated by commas')
          }
          return { name, brand, type }
        })

      const response = await fetch(`${API_URL}/process-boq-text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ items }),
      })

      if (!response.ok) throw new Error('BOQ processing failed')
      
      const data: BoqResult[] = await response.json()
      setResults(data)
      
      if (data.some(result => result.status === 'not_found')) {
        toast({
          title: "Warning",
          description: "Some items had no matches. Please check the results carefully.",
          variant: "destructive"
        })
      } else {
        toast({
          title: "Success",
          description: "All items processed successfully",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to process BOQ",
        variant: "destructive"
      })
    } finally {
      setIsProcessing(false)
    }
  }

  const getPdfLink = (pageRef: { file_path: string; page_numbers: number[] }) => {
    if (!pageRef?.page_numbers?.length) return '#'
    return `${STORAGE_URL}/${pageRef.file_path}#page=${pageRef.page_numbers[0]}`
  }

  const placeholder = `Butterfly Keramik, Cattelan Italia, tavolo
Pattie, Minotti, poltrona`

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Process Bill of Quantities</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="prose dark:prose-invert">
            <h3 className="text-lg font-medium">How it works</h3>
            <ol className="list-decimal list-inside space-y-1">
              <li>Enter products manually below</li>
              <li>The system will match each item to products in the database</li>
              <li>Review matches and find pricing in the referenced catalogs</li>
            </ol>
          </div>

          <form onSubmit={handleProcessBoq} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">
                Enter Products (one per line)
              </label>
              <p className="text-sm text-muted-foreground">
                Format: product name, brand name, product type
              </p>
              <Textarea
                value={boqText}
                onChange={(e) => setBoqText(e.target.value)}
                placeholder={placeholder}
                rows={6}
              />
            </div>
            <Button type="submit" disabled={isProcessing}>
              {isProcessing ? 'Processing...' : 'Process Items'}
            </Button>
          </form>

          {results.length > 0 && (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>BOQ Item</TableHead>
                    <TableHead>Matched Product</TableHead>
                    <TableHead>Reference Page</TableHead>
                  </TableRow>   
                </TableHeader>
                <TableBody>
                  {results.map((result, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <div className="space-y-1">
                          <div className="font-medium">{result.boqItem.name}</div>
                          <div className="text-sm text-muted-foreground">
                            Brand: {result.boqItem.brand}<br/>
                            Type: {result.boqItem.type}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        {result.matches?.length > 0 ? (
                          <Select
                            value={result.selectedMatch?.id?.toString() || ''}
                            onValueChange={(value) => {
                              const match = result.matches?.find(m => m.id.toString() === value)
                              if (match) {
                                const newResults = [...results]
                                newResults[index] = {
                                  ...newResults[index],
                                  selectedMatch: match
                                }
                                setResults(newResults)
                              }
                            }}
                          >
                            <SelectTrigger className="w-full">
                              <SelectValue>
                                {result.selectedMatch ? 
                                  `${result.selectedMatch.product_name} (${result.selectedMatch.brand_name})` :
                                  'Loading...'
                                }
                              </SelectValue>
                            </SelectTrigger>
                            <SelectContent>
                              {result.matches?.map(match => (
                                <SelectItem key={match.id} value={match.id?.toString() || ''}>
                                  {match.product_name} ({match.brand_name})
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        ) : (
                          <span className="text-muted-foreground">No matches found</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {result.selectedMatch?.page_reference && (
                          <Button
                            variant="link"
                            asChild
                          >
                            <a
                              href={getPdfLink(result.selectedMatch.page_reference)}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              View in Catalog
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
