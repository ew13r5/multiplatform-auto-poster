import type { ReactNode } from 'react'

interface CardProps {
  title?: string
  headerAction?: ReactNode
  children: ReactNode
}

export default function Card({ title, headerAction, children }: CardProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      {(title || headerAction) && (
        <div className="flex items-center justify-between mb-4">
          {title && <h2 className="text-lg font-semibold">{title}</h2>}
          {headerAction}
        </div>
      )}
      {children}
    </div>
  )
}
