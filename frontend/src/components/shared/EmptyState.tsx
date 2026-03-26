import type { LucideIcon } from 'lucide-react'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  action?: {
    label: string
    onClick: () => void
  }
}

export default function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Icon size={48} className="text-gray-400" />
      <h3 className="text-lg font-medium text-gray-900 mt-4">{title}</h3>
      <p className="text-sm text-gray-500 mt-1">{description}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg mt-4"
        >
          {action.label}
        </button>
      )}
    </div>
  )
}
