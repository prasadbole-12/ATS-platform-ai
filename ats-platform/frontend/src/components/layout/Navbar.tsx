import { useLocation } from 'react-router-dom'
import { Bell, Search } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  '/': { title: 'Dashboard', subtitle: 'Overview of your ATS platform' },
  '/upload': { title: 'Upload Resume', subtitle: 'Parse and add new candidates' },
  '/candidates': { title: 'Candidates', subtitle: 'Browse and manage all candidates' },
  '/jobs': { title: 'Job Descriptions', subtitle: 'Manage open roles' },
  '/rankings': { title: 'Rankings', subtitle: 'AI-powered candidate ranking results' },
  '/settings': { title: 'Settings', subtitle: 'Platform configuration' },
}

export function Navbar() {
  const { pathname } = useLocation()
  const meta = pageTitles[pathname] ?? { title: 'ATS Platform', subtitle: '' }

  return (
    <header className="fixed top-0 right-0 left-64 z-30 h-16 border-b border-border bg-background/95 backdrop-blur-sm flex items-center justify-between px-6">
      <div>
        <h1 className="text-base font-semibold text-foreground leading-tight">{meta.title}</h1>
        <p className="text-xs text-muted-foreground">{meta.subtitle}</p>
      </div>
      <div className="flex items-center gap-3">
        <div className="relative hidden md:block">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search candidates..."
            className="pl-8 w-56 h-9 text-sm bg-muted border-0 focus-visible:ring-1"
          />
        </div>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-4 w-4" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-primary" />
        </Button>
        <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center">
          <span className="text-xs font-semibold text-primary-foreground">HR</span>
        </div>
      </div>
    </header>
  )
}
