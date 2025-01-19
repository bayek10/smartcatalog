'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { useToast } from "@/hooks/use-toast"
import { API_URL } from '@/lib/config'

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const { toast } = useToast()
  
  const handleFileSelect = (file: File) => {
    if (!file || file.type !== 'application/pdf') {
      toast({
        title: "Invalid file",
        description: "Please upload a PDF file",
        variant: "destructive"
      })
      return
    }
    setSelectedFile(file)
  }

  const handleProcessFile = async () => {
    if (!selectedFile) return

    setIsUploading(true)
    setProgress(0)

    const formData = new FormData()
    formData.append('file', selectedFile)
    alert("API: "+API_URL)

    try {
      const response = await fetch(`${API_URL}/upload-pdf`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) throw new Error('Upload failed')

      setProgress(100)
      toast({
        title: "Success!",
        description: "PDF processed successfully",
      })

    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to process PDF",
        variant: "destructive"
      })
    } finally {
      setIsUploading(false)
      setSelectedFile(null)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload PDF Catalog</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div 
          className="border-2 border-dashed rounded-lg p-6 text-center hover:border-primary/50 transition-colors"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault()
            const file = e.dataTransfer.files[0]
            handleFileSelect(file)
          }}
        >
          <input
            type="file"
            accept=".pdf"
            className="hidden"
            id="pdf-upload"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) handleFileSelect(file)
            }}
          />
          <label
            htmlFor="pdf-upload"
            className="cursor-pointer"
          >
            <div className="text-muted-foreground">
              <p className="text-sm">Drop your PDF here or click to upload</p>
              <p className="text-xs mt-1">Supported format: PDF</p>
              {selectedFile && (
                <p className="text-sm mt-2 text-primary">Selected: {selectedFile.name}</p>
              )}
            </div>
          </label>
        </div>

        <Button 
          className="w-full"
          disabled={isUploading || !selectedFile}
          onClick={handleProcessFile}
        >
          {isUploading ? 'Processing...' : 'Process PDF'}
        </Button>

        {isUploading && (
          <div className="space-y-2">
            <Progress value={progress} />
            <p className="text-sm text-muted-foreground text-center">
              Processing PDF...
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}