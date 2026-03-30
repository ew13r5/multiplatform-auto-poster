import { NavLink } from 'react-router-dom'
import { LayoutDashboard, ListTodo, Calendar, BarChart3, Settings } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

const links: Array<{ to: string; label: string; icon: LucideIcon }> = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/queue', label: 'Queue', icon: ListTodo },
  { to: '/schedule', label: 'Schedule', icon: Calendar },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar() {
  return (
    <aside className="w-56 bg-gray-900 text-white fixed top-0 left-0 h-screen p-4 z-30">
      <h2 className="text-lg font-bold mb-6 px-2">Auto Poster</h2>
      <nav className="space-y-1">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-800'
              }`
            }
          >
            <link.icon size={18} />
            <span>{link.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
