import { ReactNode } from 'react'
import Sidebar from './Sidebar'
import ModeBanner from './ModeBanner'

interface AppLayoutProps {
  children: ReactNode
  mode?: string
}

export default function AppLayout({ children, mode = 'development' }: AppLayoutProps) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <ModeBanner mode={mode} />
        <main className="flex-1">{children}</main>
      </div>
    </div>
  )
}
