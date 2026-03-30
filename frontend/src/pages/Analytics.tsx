import { useEffect, useMemo, useState } from 'react'
import { Heart, MessageCircle, Share2, TrendingUp } from 'lucide-react'
import type { PostEngagement, HeatmapCell } from '../types/analytics'
import type { Page } from '../types/page'
import { getEngagement, getBestTime } from '../api/analytics'
import { getPages } from '../api/pages'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import ErrorState from '../components/shared/ErrorState'
import Card from '../components/shared/Card'
import EngagementChart from '../components/Analytics/EngagementChart'
import BestTimeHeatmap from '../components/Analytics/BestTimeHeatmap'
import TopPostsTable from '../components/Analytics/TopPostsTable'

const dayOptions = [7, 30, 90]

export default function Analytics() {
  const [posts, setPosts] = useState<PostEngagement[]>([])
  const [cells, setCells] = useState<HeatmapCell[]>([])
  const [pages, setPages] = useState<Page[]>([])
  const [selectedPageId, setSelectedPageId] = useState('')
  const [days, setDays] = useState(30)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    const params: { page_id?: string; days?: number; limit?: number } = { days, limit: 50 }
    if (selectedPageId) params.page_id = selectedPageId

    const bestTimeParams: { page_id?: string } = {}
    if (selectedPageId) bestTimeParams.page_id = selectedPageId

    Promise.all([getEngagement(params), getBestTime(bestTimeParams), getPages()])
      .then(([postsData, cellsData, pagesData]) => {
        if (cancelled) return
        setPosts(postsData)
        setCells(cellsData)
        setPages(pagesData)
      })
      .catch((err) => {
        if (cancelled) return
        setError(err instanceof Error ? err.message : 'Failed to load analytics')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => { cancelled = true }
  }, [selectedPageId, days])

  const stats = useMemo(() => {
    const totalLikes = posts.reduce((s, p) => s + p.likes, 0)
    const totalComments = posts.reduce((s, p) => s + p.comments, 0)
    const totalShares = posts.reduce((s, p) => s + p.shares, 0)
    const totalEngagement = totalLikes + totalComments + totalShares
    return { totalLikes, totalComments, totalShares, totalEngagement, postCount: posts.length }
  }, [posts])

  if (loading) return <div className="p-6 flex justify-center"><LoadingSpinner /></div>
  if (error) return <div className="p-6"><ErrorState message={error} onRetry={() => setDays((d) => d)} /></div>

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Analytics</h1>
        <div className="flex gap-2 items-center">
          <select
            value={selectedPageId}
            onChange={(e) => setSelectedPageId(e.target.value)}
            className="border rounded-lg px-3 py-1.5 text-sm"
          >
            <option value="">All Channels</option>
            {pages.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          <div className="inline-flex rounded-lg border border-gray-200 overflow-hidden">
            {dayOptions.map((d) => (
              <button
                key={d}
                onClick={() => setDays(d)}
                className={`px-3 py-1.5 text-sm ${
                  days === d
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                {d}d
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
            <TrendingUp size={14} />
            Total Engagement
          </div>
          <div className="text-2xl font-bold">{stats.totalEngagement.toLocaleString('en-US')}</div>
          <div className="text-xs text-gray-400 mt-0.5">{stats.postCount} posts</div>
        </div>
        <div className="bg-white rounded-xl border p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
            <Heart size={14} className="text-red-400" />
            Likes
          </div>
          <div className="text-2xl font-bold">{stats.totalLikes.toLocaleString('en-US')}</div>
        </div>
        <div className="bg-white rounded-xl border p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
            <MessageCircle size={14} className="text-blue-400" />
            Comments
          </div>
          <div className="text-2xl font-bold">{stats.totalComments.toLocaleString('en-US')}</div>
        </div>
        <div className="bg-white rounded-xl border p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
            <Share2 size={14} className="text-green-400" />
            Shares
          </div>
          <div className="text-2xl font-bold">{stats.totalShares.toLocaleString('en-US')}</div>
        </div>
      </div>

      {/* Chart + Heatmap */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card title="Top Posts by Engagement" headerAction={
          <div className="flex gap-2 text-xs text-gray-400">
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-500" />Likes</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500" />Comments</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-orange-500" />Shares</span>
          </div>
        }>
          <div className="lg:col-span-2">
            <EngagementChart posts={posts} />
          </div>
        </Card>
        <Card title="Best Posting Time">
          <BestTimeHeatmap cells={cells} />
        </Card>
      </div>

      {/* Top Posts */}
      <Card title="Top Performing Posts">
        <TopPostsTable posts={posts} />
      </Card>
    </div>
  )
}
