import { redirect } from 'next/navigation'

export default function Dashboard() {
  // Redirect to upload page by default
  redirect('/dashboard/upload')
}