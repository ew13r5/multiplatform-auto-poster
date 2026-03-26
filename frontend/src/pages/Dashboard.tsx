import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Globe, ListTodo, CheckCircle, XCircle, Activity } from 'lucide-react'
import { useDashboardData } from '../hooks/useDashboardData'
import { useWebSocket } from '../hooks/useWebSocket'
import { timeAgo } from '../utils/timeAgo'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import ErrorState from '../components/shared/ErrorState'
import EmptyState from '../components/shared/EmptyState'
import Card from '../components/shared/Card'

function isToday(dateStr: string): boolean {
  return new Date(dateStr).toDateString() === new Date().toDateString()
}

export default function Dashboard() {
  const { health, pages, logEntries, loading, error, refetch } = useDashboardData()
  const { lastEvent } = useWebSocket()
  const navigate = useNavigate()
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (!lastEvent) return
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => refetch(), 2000)
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current) }
  }, [lastEvent, refetch])

  if (loading) return <div className="p-6"><LoadingSpinner size="lg" /></div>
  if (error) return <div className="p-6"><ErrorState message={error} onRetry={refetch} /></div>

  const totalPages = pages.length
  const queuedPosts = pages.reduce((sum, p) => sum + p.queued_count, 0)
  const publishedToday = logEntries.filter(
    (e) => e.result === 'success' && e.attempted_at && isToday(e.attempted_at)
  ).length
  const failedToday = logEntries.filter(
    (e) => e.result.includes('error') && e.attempted_at && isToday(e.attempted_at)
  ).length

  const stats = [
    { label: 'Total Pages', value: totalPages, icon: Globe, bg: 'bg-blue-100', text: 'text-blue-600' },
    { label: 'Queued Posts', value: queuedPosts, icon: ListTodo, bg: 'bg-yellow-100', text: 'text-yellow-600' },
    { label: 'Published Today', value: publishedToday, icon: CheckCircle, bg: 'bg-green-100', text: 'text-green-600' },
    { label: 'Failed Today', value: failedToday, icon: XCircle, bg: 'bg-red-100', text: 'text-red-600' },
  ]

  const statusBadge = (status: string) => {
    const colors = status === 'healthy'
      ? 'bg-green-100 text-green-700'
      : status === 'degraded'
        ? 'bg-yellow-100 text-yellow-700'
        : 'bg-red-100 text-red-700'
    return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors}`}>{status}</span>
  }

  return (
    <div className="p-6 space-y-6">
      {/* Quick Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <div className="flex items-center gap-4">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${stat.bg}`}>
                <stat.icon size={24} className={stat.text} />
              </div>
              <div>
                <p className="text-3xl font-bold">{stat.value}</p>
                <p className="text-sm text-gray-500">{stat.label}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* System Health */}
      {health && (
        <Card
          title="System Health"
          headerAction={
            <div className="flex gap-2">
              {statusBadge(health.status)}
              {health.mode === 'development' && (
                <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-700">
                  Development Mode
                </span>
              )}
            </div>
          }
        >
          <div className="flex gap-8">
            {Object.entries(health.checks).map(([service, ok]) => (
              <div key={service} className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${ok ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm font-medium capitalize">{service}</span>
                <span className={`text-sm ${ok ? 'text-green-600' : 'text-red-600'}`}>
                  {ok ? 'Connected' : 'Down'}
                </span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Connected Pages */}
      <Card
        title="Connected Pages"
        headerAction={
          <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
            {pages.length}
          </span>
        }
      >
        {pages.length === 0 ? (
          <EmptyState
            icon={Globe}
            title="No pages connected"
            description="Connect a Facebook Page to start publishing"
            action={{ label: 'Go to Settings', onClick: () => navigate('/settings') }}
          />
        ) : (
          <div className="divide-y">
            {pages.map((page) => (
              <div key={page.id} className="flex items-center justify-between py-3 first:pt-0 last:pb-0">
                <div>
                  <p className="font-medium">{page.name}</p>
                  {page.category && <p className="text-sm text-gray-500">{page.category}</p>}
                </div>
                <div className="flex items-center gap-4">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                    page.token_status === 'configured'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {page.token_status === 'configured' ? 'Configured' : 'Missing'}
                  </span>
                  <span className="text-sm text-gray-500">{page.queued_count} queued</span>
                  <span className="text-sm text-gray-400">{timeAgo(page.last_published_at)}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Recent Activity */}
      <Card title="Recent Activity">
        {logEntries.length === 0 ? (
          <EmptyState
            icon={Activity}
            title="No publishing activity yet"
            description=""
          />
        ) : (
          <div className="space-y-3">
            {logEntries.slice(0, 10).map((entry, i) => (
              <div key={i} className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{entry.page_name}</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      entry.result === 'success'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                    }`}>
                      {entry.result}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 truncate">{entry.content_preview}</p>
                  {entry.error_message && (
                    <p className="text-sm text-red-500">{entry.error_message}</p>
                  )}
                </div>
                <span className="text-xs text-gray-400 shrink-0 ml-4">
                  {timeAgo(entry.attempted_at)}
                </span>
              </div>
            ))}
            <button
              onClick={() => navigate('/settings')}
              className="text-sm text-blue-500 hover:text-blue-600"
            >
              View all logs
            </button>
          </div>
        )}
      </Card>
    </div>
  )
}
