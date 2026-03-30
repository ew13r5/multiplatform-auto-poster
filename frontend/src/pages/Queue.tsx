import { useCallback, useEffect, useRef, useState } from 'react'
import { List, Clock } from 'lucide-react'
import type { Post } from '../types/post'
import type { Page } from '../types/page'
import { getPosts, deletePost, publishNow, reorderPosts, retryPost } from '../api/posts'
import { getPages } from '../api/pages'
import { useToast } from '../components/shared/Toast'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import ErrorState from '../components/shared/ErrorState'
import Card from '../components/shared/Card'
import StatusTabs from '../components/ContentQueue/StatusTabs'
import PostList from '../components/ContentQueue/PostList'
import TimelineView from '../components/ContentQueue/TimelineView'
import PostEditorModal from '../components/ContentQueue/PostEditorModal'
import BulkImportModal from '../components/ContentQueue/BulkImportModal'

export default function Queue() {
  const toast = useToast()

  const [posts, setPosts] = useState<Post[]>([])
  const [total, setTotal] = useState(0)
  const [pages, setPages] = useState<Page[]>([])
  const [selectedPageId, setSelectedPageId] = useState('')
  const [selectedStatus, setSelectedStatus] = useState('')
  const [viewMode, setViewMode] = useState<'list' | 'timeline'>('timeline')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editorOpen, setEditorOpen] = useState(false)
  const [editingPost, setEditingPost] = useState<Post | null>(null)
  const [bulkImportOpen, setBulkImportOpen] = useState(false)
  const [refreshCounter, setRefreshCounter] = useState(0)

  const prevOrderRef = useRef<Post[]>([])
  const refresh = useCallback(() => setRefreshCounter((c) => c + 1), [])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    const params: Record<string, string | number> = { limit: 50 }
    if (selectedPageId) params.page_id = selectedPageId
    if (selectedStatus) params.status = selectedStatus

    Promise.all([getPosts(params), getPages()])
      .then(([postsData, pagesData]) => {
        if (cancelled) return
        setPosts(postsData.posts)
        setTotal(postsData.total)
        setPages(pagesData)
      })
      .catch((err) => {
        if (cancelled) return
        setError(err instanceof Error ? err.message : 'Failed to load data')
      })
      .finally(() => { if (!cancelled) setLoading(false) })

    return () => { cancelled = true }
  }, [selectedPageId, selectedStatus, refreshCounter])

  const pageMap = new Map(pages.map((p) => [p.id, p.name]))

  function handleEdit(post: Post) { setEditingPost(post); setEditorOpen(true) }
  function handleNewPost() { setEditingPost(null); setEditorOpen(true) }

  async function handleDelete(id: string) {
    if (!window.confirm('Delete this post?')) return
    try { await deletePost(id); toast.success('Post deleted'); refresh() }
    catch { toast.error('Failed to delete post') }
  }

  async function handlePublish(id: string) {
    if (!window.confirm('Publish now?')) return
    try { await publishNow(id); toast.success('Publishing started'); refresh() }
    catch { toast.error('Failed to publish') }
  }

  async function handleRetry(id: string) {
    try { await retryPost(id); toast.success('Post queued for retry'); refresh() }
    catch { toast.error('Failed to retry') }
  }

  async function handleReorder(items: { id: string; order_index: number }[]) {
    prevOrderRef.current = [...posts]
    const reordered = items.map((item) => posts.find((p) => p.id === item.id)!).filter(Boolean)
    setPosts(reordered)
    try { await reorderPosts(items) }
    catch { setPosts(prevOrderRef.current); toast.error('Failed to reorder') }
  }

  async function handleLoadMore() {
    const params: Record<string, string | number> = { limit: 50, offset: posts.length }
    if (selectedPageId) params.page_id = selectedPageId
    if (selectedStatus) params.status = selectedStatus
    try { const data = await getPosts(params); setPosts((prev) => [...prev, ...data.posts]) }
    catch { toast.error('Failed to load more posts') }
  }

  if (loading) return <div className="p-6 flex justify-center"><LoadingSpinner /></div>
  if (error) return <div className="p-6"><ErrorState message={error} onRetry={refresh} /></div>

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Content Queue</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setBulkImportOpen(true)}
            className="px-4 py-2 text-sm border rounded-lg hover:bg-gray-50"
          >
            Bulk Import
          </button>
          <button
            onClick={handleNewPost}
            className="px-4 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            + New Post
          </button>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
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
          <StatusTabs selected={selectedStatus} onChange={setSelectedStatus} />
        </div>

        {/* View toggle */}
        <div className="inline-flex rounded-lg border border-gray-200 overflow-hidden">
          <button
            onClick={() => setViewMode('timeline')}
            className={`px-3 py-1.5 text-sm flex items-center gap-1 ${
              viewMode === 'timeline' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Clock size={14} /> Timeline
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`px-3 py-1.5 text-sm flex items-center gap-1 ${
              viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            <List size={14} /> List
          </button>
        </div>
      </div>

      {viewMode === 'timeline' ? (
        <TimelineView
          posts={posts}
          pageMap={pageMap}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onPublish={handlePublish}
          onRetry={handleRetry}
        />
      ) : (
        <Card>
          <PostList
            posts={posts}
            pageMap={pageMap}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onPublish={handlePublish}
            onRetry={handleRetry}
            onReorder={handleReorder}
          />
          {total > posts.length && (
            <div className="py-4 text-center">
              <button onClick={handleLoadMore} className="px-4 py-2 text-sm text-blue-500 hover:text-blue-700">
                Load More
              </button>
            </div>
          )}
        </Card>
      )}

      <PostEditorModal
        isOpen={editorOpen}
        onClose={() => setEditorOpen(false)}
        onSave={() => { setEditorOpen(false); refresh() }}
        post={editingPost}
        pages={pages}
      />
      <BulkImportModal
        isOpen={bulkImportOpen}
        onClose={() => setBulkImportOpen(false)}
        onImported={() => { setBulkImportOpen(false); refresh() }}
      />
    </div>
  )
}
