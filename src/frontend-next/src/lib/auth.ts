// This is a simple auth implementation - replace with your preferred auth solution later
const DEMO_USER = {
    email: 'f@u.com',
    // In production, use proper password hashing
    password: 'fu' 
  }
  
  export async function authenticate(email: string, password: string) {
    if (email === DEMO_USER.email && password === DEMO_USER.password) {
      // In production, generate proper JWT tokens
      return { token: 'demo-token' }
    }
    throw new Error('Invalid credentials')
  }
  
  export function isAuthenticated(token: string) {
    return token === 'demo-token'
  }