import Link from 'next/link'
import Image from 'next/image'
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <nav className="fixed top-0 left-0 right-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="px-6 mx-auto max-w-7xl flex h-14 items-center justify-between">
          <div className="flex items-center gap-2">
            <Image
              src="/logo.png"
              alt="Smart Catalog Logo"
              width={240}
              height={42}
              className="h-10 w-auto"
            />
          </div>
          <Link href="/login">
            <Button variant="default">Sign in</Button>
          </Link>
        </div>
      </nav>

      <main className="px-6 mx-auto max-w-7xl">
        <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] py-10">
          <Card className="w-full max-w-4xl border-none shadow-none">
            <CardContent className="p-0 space-y-8">
              <h1 className="text-6xl font-normal tracking-tight text-center">
                Digitize your product catalog & price lists
              </h1>
              <p className="text-xl text-muted-foreground text-center max-w-2xl mx-auto">
                Use our AI-powered engine to transform your PDF product catalogs into a database in minutes. Save hours of manually going through PDFs to find information.
              </p>
              <div className="flex justify-center">
                <Link href="mailto:h5sami@uwaterloo.ca?subject=Inquiry%20about%20AI%20Data%20Extraction%20Software">
                  <Button size="lg">Reach out</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}