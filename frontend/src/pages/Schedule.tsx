import { useCallback, useEffect, useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import type { Post } from '../types/post'
import type { Page } from '../types/page'
import { getPosts } from '../api/posts'
import { getPages } from '../api/pages'
import { togglePause } from '../api/schedule'
import { useToast } from '../components/shared/Toast'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import ErrorState from '../components/shared/ErrorState'
import WeekCalendar from '../components/Schedule/WeekCalendar'
import PostEditorModal from '../components/ContentQueue/PostEditorModal'

function getMonday(d: Date): Date {
  const date = new Date(d)
  const day = date.getDay()
  const diff = day === 0 ? -6 : 1 - day
  date.setDate(date.getDate() + diff)
  date.setHours(0, 0, 0, 0)
  return date
}

function formatWeekRange(start: Date): string {
  const end = new Date(start)
  end.setDate(end.getDate() + 6)
  const opts: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric' }
  if (start.getMonth() === end.getMonth()) {
    return `${start.toLocaleDateString('en-US', { month: 'long', day: 'numeric' })} – ${end.getDate()}, ${start.getFullYear()}`
  }
  return `${start.toLocaleDateString('en-US', opts)} – ${end.toLocaleDateString('en-US', opts)}, ${start.getFullYear()}`
}

export default function Schedule() {
  const toast = useToast()

  const [posts, setPosts] = useState<Post[]>([])
  const [pages, setPages] = useState<Page[]>([])
  const [weekStart, setWeekStart] = useState(() => getMonday(new Date()))
  const [paused, setPaused] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editorOpen, setEditorOpen] = useState(false)
  const [editingPost, setEditingPost] = useState<Post | null>(null)
  const [refreshCounter, setRefreshCounter] = useState(0)

  const refresh = useCallback(() => setRefreshCounter((c) => c + 1), [])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    Promise.all([
      getPosts({ limit: 200 }),
      getPages(),
    ])
      .then(([postsData, pagesData]) => {
        if (cancelled) return
        setPosts(postsData.posts)
        setPages(pagesData)
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load')
      })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [refreshCounter])

  const pageMap = new Map(pages.map((p) => [p.id, p.name]))
  const platformMap = new Map(pages.map((p) => [p.id, p.platform || 'facebook']))

  function prevWeek() {
    setWeekStart((w) => { const d = new Date(w); d.setDate(d.getDate() - 7); return d })
  }
  function nextWeek() {
    setWeekStart((w) => { const d = new Date(w); d.setDate(d.getDate() + 7); return d })
  }
  function goToday() {
    setWeekStart(getMonday(new Date()))
  }

  function handleSlotClick(_date: Date) {
    setEditingPost(null)
    setEditorOpen(true)
  }

  function handlePostClick(post: Post) {
    setEditingPost(post)
    setEditorOpen(true)
  }

  async function handlePauseToggle() {
    try {
      const result = await togglePause(!paused)
      setPaused(result.paused)
      toast.success(result.paused ? 'Publishing paused' : 'Publishing resumed')
    } catch {
      toast.error('Failed to toggle pause')
    }
  }

  if (loading) return <div className="p-6 flex justify-center"><LoadingSpinner /></div>
  if (error) return <div className="p-6"><ErrorState message={error} onRetry={refresh} /></div>

  return (
    <div className="h-screen flex flex-col">
      {/* Sticky header */}
      <div className="sticky top-0 z-20 bg-gray-50 px-6 pt-4 pb-2 space-y-3 border-b">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Schedule</h1>
          <button
            onClick={handlePauseToggle}
            className={`px-4 py-1.5 text-sm rounded-lg ${
              paused ? 'bg-green-500 hover:bg-green-600 text-white' : 'bg-yellow-500 hover:bg-yellow-600 text-white'
            }`}
          >
            {paused ? 'Resume' : 'Pause'}
          </button>
        </div>

        {paused && (
          <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 p-3 rounded-lg text-sm">
            Publishing is paused.
          </div>
        )}

        {/* Week navigation */}
        <div className="flex items-center justify-between bg-white rounded-lg border px-4 py-2.5">
          <div className="flex items-center gap-2">
            <button onClick={prevWeek} className="p-1.5 rounded-lg hover:bg-gray-100">
              <ChevronLeft size={18} />
            </button>
            <button onClick={nextWeek} className="p-1.5 rounded-lg hover:bg-gray-100">
              <ChevronRight size={18} />
            </button>
            <span className="text-lg font-semibold ml-2">{formatWeekRange(weekStart)}</span>
          </div>
          <button onClick={goToday} className="text-sm text-blue-600 hover:text-blue-700 font-medium">
            Today
          </button>
        </div>
      </div>

      {/* Scrollable calendar */}
      <div className="flex-1 overflow-y-auto px-6 py-3">
        <div className="bg-white rounded-lg border overflow-hidden">
          <WeekCalendar
            posts={posts}
            weekStart={weekStart}
            pageMap={pageMap}
            platformMap={platformMap}
            onPostClick={handlePostClick}
            onSlotClick={handleSlotClick}
          />
        </div>
      </div>

      <PostEditorModal
        isOpen={editorOpen}
        onClose={() => setEditorOpen(false)}
        onSave={() => { setEditorOpen(false); refresh() }}
        post={editingPost}
        pages={pages}
      />
    </div>
  )
}
