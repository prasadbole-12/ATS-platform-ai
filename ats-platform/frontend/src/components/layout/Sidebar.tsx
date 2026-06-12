import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  Upload,
  Trophy,
  Briefcase,
  Settings,
  Zap,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/upload', icon: Upload, label: 'Upload Resume' },
  { to: '/candidates', icon: Users, label: 'Candidates' },
  { to: '/jobs', icon: Briefcase, label: 'Job Descriptions' },
  { to: '/rankings', icon: Trophy, label: 'Rankings' },
]

export function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-40 w-64 border-r border-border bg-card flex flex-col">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2.5 px-6 border-b border-border">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
          <Zap className="h-4 w-4 text-primary-foreground" />
        </div>
        <div>
          <p className="text-sm font-semibold text-foreground leading-tight">ATS Platform</p>
          <p className="text-[10px] text-muted-foreground">Candidate Ranking</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-0.5">
        <p className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
          Main Menu
        </p>
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'group flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-all',
                isActive
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-muted-foreground hover:bg-accent hover:text-foreground',
              )
            }
          >
            <Icon className="h-4 w-4 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Bottom */}
      <div className="border-t border-border p-3">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-all',
              isActive
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-accent hover:text-foreground',
            )
          }
        >
          <Settings className="h-4 w-4" />
          Settings
        </NavLink>
        <div className="mt-3 px-3 py-2 rounded-md bg-muted/50">
          <p className="text-xs font-medium text-foreground">ATS Platform</p>
          <p className="text-[10px] text-muted-foreground">Day 1 Foundation · v1.0.0</p>
        </div>
      </div>
    </aside>
  )
}
