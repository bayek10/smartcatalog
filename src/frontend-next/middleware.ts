import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // Redirect www to non-www
  if (request.headers.get('host')?.startsWith('www.')) {
    return NextResponse.redirect(
      new URL(request.url.replace('www.', ''))
    )
  }

  // Handle dashboard routes
  if (pathname.startsWith('/dashboard')) {
    // Check if user is authenticated
    const token = request.cookies.get('auth-token')
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}