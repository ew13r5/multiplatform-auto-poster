import type { PostStatus } from '../../types/post'

const statusColors: Record<PostStatus, string> = {
  draft: 'bg-gray-200 text-gray-700',
  queued: 'bg-blue-100 text-blue-700',
  publishing: 'bg-yellow-100 text-yellow-700 animate-pulse',
  published: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
}

export default function StatusBadge({ status }: { status: PostStatus }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[status]}`}>
      {status}
    </span>
  )
}
