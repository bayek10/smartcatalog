'use client'

import Link from 'next/link'
import Image from 'next/image'
import { Button } from "@/components/ui/button"
import { Toaster } from "@/components/ui/toaster"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <div className="w-64 bg-card border-r flex flex-col">
        {/* Logo section */}
        <div className="p-6 border-b">
          <Image
            src="/logo.png"
            alt="Smart Catalog Logo"
            width={150}
            height={32}
            className="w-auto h-10"
          />
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-2">
          <div className="space-y-1">
            <Link href="/dashboard/upload">
              <Button 
                variant="ghost" 
                className="w-full justify-start h-10 px-3 py-2 text-sm font-medium"
              >
                <svg
                  className="mr-3 h-4 w-4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                >
                  <path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
                </svg>
                Upload & Process PDF
              </Button>
            </Link>
            <Link href="/dashboard/library">
              <Button 
                variant="ghost" 
                className="w-full justify-start h-10 px-3 py-2 text-sm font-medium"
              >
                <svg
                  className="mr-3 h-4 w-4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                >
                  <path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
                </svg>
                Product Library
              </Button>
            </Link>
            <Link href="/dashboard/process-boq">
              <Button 
                variant="ghost" 
                className="w-full justify-start h-10 px-3 py-2 text-sm font-medium"
              >
                <svg
                  className="mr-3 h-4 w-4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                >
                  <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
                </svg>
                Process BOQ
              </Button>
            </Link>
          </div>
        </nav>

        {/* User section - optional */}
        <div className="p-4 border-t">
          <Button 
            variant="ghost" 
            className="w-full justify-start h-10 px-3 py-2 text-sm font-medium"
            onClick={() => {
              document.cookie = 'auth-token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
              window.location.href = '/login';
            }}
          >
            <svg
              className="mr-3 h-4 w-4"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
            >
              <path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>
            Sign out
          </Button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 min-h-screen bg-background">
        <main className="p-6">
          {children}
        </main>
      </div>
      <Toaster />
    </div>
  )
}