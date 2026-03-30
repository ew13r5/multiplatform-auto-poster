import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { BarChart3 } from 'lucide-react'
import type { PostEngagement } from '../../types/analytics'
import EmptyState from '../shared/EmptyState'

interface EngagementChartProps {
  posts: PostEngagement[]
}

export default function EngagementChart({ posts }: EngagementChartProps) {
  if (posts.length === 0) {
    return (
      <EmptyState
        icon={BarChart3}
        title="No engagement data"
        description="Publish posts to see analytics"
      />
    )
  }

  const data = posts
    .map((p) => ({ ...p, total: p.likes + p.comments + p.shares }))
    .sort((a, b) => b.total - a.total)
    .slice(0, 8)
    .map((p, i) => ({
      name: `#${i + 1}`,
      likes: p.likes,
      comments: p.comments,
      shares: p.shares,
    }))

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} barCategoryGap="20%">
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
        <XAxis dataKey="name" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 12 }} axisLine={false} tickLine={false} width={35} />
        <Tooltip
          contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '13px' }}
        />
        <Bar dataKey="likes" stackId="a" fill="#3b82f6" radius={[0, 0, 0, 0]} />
        <Bar dataKey="comments" stackId="a" fill="#22c55e" />
        <Bar dataKey="shares" stackId="a" fill="#f97316" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
