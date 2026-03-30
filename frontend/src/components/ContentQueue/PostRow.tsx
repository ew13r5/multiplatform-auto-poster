import { FileText, Image, Link, Pencil, Trash2, Send, GripVertical, Clock, RotateCcw } from 'lucide-react'
import type { Post } from '../../types/post'
import StatusBadge from './StatusBadge'

interface PostRowProps {
  post: Post
  pageName?: string
  onEdit: (post: Post) => void
  onDelete: (id: string) => void
  onPublish: (id: string) => void
  onRetry?: (id: string) => void
  dragHandleProps?: Record<string, unknown>
}

const typeIcons = {
  text: FileText,
  photo: Image,
  link: Link,
}

export default function PostRow({ post, pageName, onEdit, onDelete, onPublish, onRetry, dragHandleProps }: PostRowProps) {
  const Icon = typeIcons[post.post_type] || FileText
  const preview = post.content_text.length > 80
    ? post.content_text.slice(0, 80) + '…'
    : post.content_text

  return (
    <div className="flex items-center gap-3 py-3 border-b last:border-b-0">
      {dragHandleProps && (
        <span {...dragHandleProps} className="cursor-grab text-gray-400 hover:text-gray-600">
          <GripVertical size={16} />
        </span>
      )}
      <Icon size={16} className="text-gray-400 shrink-0" />
      <span className="text-sm flex-1 truncate">{preview}</span>
      <StatusBadge status={post.status} />
      {post.scheduled_at && (
        <span className="text-xs text-blue-500 shrink-0 flex items-center gap-1">
          <Clock size={12} />
          {new Date(post.scheduled_at).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
        </span>
      )}
      {pageName && <span className="text-sm text-gray-500 shrink-0">{pageName}</span>}
      <div className="flex gap-1 shrink-0">
        {(post.status === 'draft' || post.status === 'queued') && (
          <>
            <button
              onClick={() => onEdit(post)}
              className="p-1 rounded hover:bg-gray-100"
              aria-label="Edit"
            >
              <Pencil size={14} />
            </button>
            <button
              onClick={() => onDelete(post.id)}
              className="p-1 rounded hover:bg-gray-100"
              aria-label="Delete"
            >
              <Trash2 size={14} />
            </button>
          </>
        )}
        {post.status === 'queued' && (
          <button
            onClick={() => onPublish(post.id)}
            className="p-1 rounded hover:bg-gray-100"
            aria-label="Publish now"
          >
            <Send size={14} />
          </button>
        )}
        {post.status === 'failed' && onRetry && (
          <button
            onClick={() => onRetry(post.id)}
            className="p-1 rounded hover:bg-orange-50 text-orange-500"
            aria-label="Retry"
          >
            <RotateCcw size={14} />
          </button>
        )}
      </div>
    </div>
  )
}
