import { useMemo } from 'react'
import { Clock, Send, Pencil, Trash2, FileText, Image, Link, CheckCircle2, AlertCircle, Loader, RotateCcw } from 'lucide-react'
import type { Post } from '../../types/post'

interface TimelineViewProps {
  posts: Post[]
  pageMap: Map<string, string>
  onEdit: (post: Post) => void
  onDelete: (id: string) => void
  onPublish: (id: string) => void
  onRetry?: (id: string) => void
}

const statusConfig = {
  draft: { color: 'bg-gray-400', label: 'Draft', icon: FileText },
  queued: { color: 'bg-blue-500', label: 'Queued', icon: Clock },
  publishing: { color: 'bg-yellow-500', label: 'Publishing', icon: Loader },
  published: { color: 'bg-green-500', label: 'Published', icon: CheckCircle2 },
  failed: { color: 'bg-red-500', label: 'Failed', icon: AlertCircle },
}

const typeIcons = { text: FileText, photo: Image, link: Link }

function groupByDay(posts: Post[]): Map<string, Post[]> {
  const groups = new Map<string, Post[]>()
  for (const post of posts) {
    const dateKey = post.scheduled_at
      ? new Date(post.scheduled_at).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
      : 'Unscheduled'
    if (!groups.has(dateKey)) groups.set(dateKey, [])
    groups.get(dateKey)!.push(post)
  }
  return groups
}

function isToday(dateStr: string): boolean {
  const today = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
  return dateStr === today
}

export default function TimelineView({ posts, pageMap, onEdit, onDelete, onPublish, onRetry }: TimelineViewProps) {
  const groups = useMemo(() => {
    const sorted = [...posts].sort((a, b) => {
      if (!a.scheduled_at && !b.scheduled_at) return 0
      if (!a.scheduled_at) return 1
      if (!b.scheduled_at) return -1
      return new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime()
    })
    return groupByDay(sorted)
  }, [posts])

  return (
    <div className="space-y-6">
      {Array.from(groups.entries()).map(([dateLabel, dayPosts]) => (
        <div key={dateLabel}>
          {/* Day separator */}
          <div className="flex items-center gap-3 mb-3">
            <div className="h-px flex-1 bg-gray-200" />
            <span className={`text-sm font-semibold px-2 ${
              isToday(dateLabel) ? 'text-blue-600' : 'text-gray-500'
            }`}>
              {isToday(dateLabel) ? `Today — ${dateLabel}` : dateLabel}
            </span>
            <div className="h-px flex-1 bg-gray-200" />
          </div>

          {/* Posts timeline */}
          <div className="relative ml-6 pl-6 border-l-2 border-gray-200 space-y-3">
            {dayPosts.map((post) => {
              const status = statusConfig[post.status] || statusConfig.draft
              const TypeIcon = typeIcons[post.post_type] || FileText
              const time = post.scheduled_at
                ? new Date(post.scheduled_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
                : null

              return (
                <div key={post.id} className="relative group">
                  {/* Timeline dot */}
                  <div className={`absolute -left-[31px] top-4 w-3 h-3 rounded-full border-2 border-white ${status.color}`} />

                  {/* Post card */}
                  <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-start gap-3">
                      {/* Time + type */}
                      <div className="shrink-0 text-center min-w-[50px]">
                        {time && (
                          <div className="text-sm font-bold text-gray-800">{time}</div>
                        )}
                        <TypeIcon size={14} className="text-gray-400 mx-auto mt-1" />
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-800">{post.content_text}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full text-white ${status.color}`}>
                            {status.label}
                          </span>
                          <span className="text-xs text-gray-400">
                            {pageMap.get(post.page_id) || ''}
                          </span>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-1 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                        {(post.status === 'draft' || post.status === 'queued') && (
                          <>
                            <button onClick={() => onEdit(post)} className="p-1.5 rounded-lg hover:bg-gray-100" aria-label="Edit">
                              <Pencil size={14} />
                            </button>
                            <button onClick={() => onDelete(post.id)} className="p-1.5 rounded-lg hover:bg-gray-100" aria-label="Delete">
                              <Trash2 size={14} />
                            </button>
                          </>
                        )}
                        {post.status === 'queued' && (
                          <button onClick={() => onPublish(post.id)} className="p-1.5 rounded-lg hover:bg-blue-50 text-blue-600" aria-label="Publish now">
                            <Send size={14} />
                          </button>
                        )}
                        {post.status === 'failed' && onRetry && (
                          <button onClick={() => onRetry(post.id)} className="p-1.5 rounded-lg hover:bg-orange-50 text-orange-500" aria-label="Retry">
                            <RotateCcw size={14} />
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      ))}
    </div>
  )
}
