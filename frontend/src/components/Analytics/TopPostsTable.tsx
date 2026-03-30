import { Heart, MessageCircle, Share2 } from 'lucide-react'
import { ListTodo } from 'lucide-react'
import type { PostEngagement } from '../../types/analytics'
import EmptyState from '../shared/EmptyState'

interface TopPostsTableProps {
  posts: PostEngagement[]
}

export default function TopPostsTable({ posts }: TopPostsTableProps) {
  if (posts.length === 0) {
    return (
      <EmptyState
        icon={ListTodo}
        title="No posts yet"
        description="Publish posts to see top performers"
      />
    )
  }

  const sorted = [...posts]
    .sort((a, b) => (b.likes + b.comments + b.shares) - (a.likes + a.comments + a.shares))
    .slice(0, 10)

  const maxTotal = sorted[0] ? sorted[0].likes + sorted[0].comments + sorted[0].shares : 1

  return (
    <div className="space-y-2">
      {sorted.map((post, i) => {
        const total = post.likes + post.comments + post.shares
        const pct = (total / maxTotal) * 100
        return (
          <div key={post.post_id} className="flex items-center gap-3 py-2.5 border-b last:border-b-0">
            <span className="text-sm font-bold text-gray-300 w-6 text-right shrink-0">{i + 1}</span>
            <div className="flex-1 min-w-0">
              <p className="text-sm truncate text-gray-800">
                {post.content_preview.length > 70
                  ? post.content_preview.slice(0, 70) + '...'
                  : post.content_preview}
              </p>
              {/* Engagement bar */}
              <div className="mt-1.5 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full" style={{ width: `${pct}%` }} />
              </div>
            </div>
            <div className="flex items-center gap-4 shrink-0 text-xs text-gray-500">
              <span className="flex items-center gap-1" title="Likes">
                <Heart size={12} className="text-red-400" />{post.likes}
              </span>
              <span className="flex items-center gap-1" title="Comments">
                <MessageCircle size={12} className="text-blue-400" />{post.comments}
              </span>
              <span className="flex items-center gap-1" title="Shares">
                <Share2 size={12} className="text-green-400" />{post.shares}
              </span>
            </div>
          </div>
        )
      })}
    </div>
  )
}
