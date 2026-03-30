import { useEffect, useState } from 'react'
import type { Post } from '../../types/post'
import type { Page } from '../../types/page'
import { createPost, updatePost } from '../../api/posts'
import { uploadImage } from '../../api/images'
import { useToast } from '../shared/Toast'
import Modal from '../shared/Modal'
import SchedulePicker from './SchedulePicker'

interface PostEditorModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: () => void
  post: Post | null
  pages: Page[]
}

function toLocalDatetime(iso?: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  const offset = d.getTimezoneOffset()
  const local = new Date(d.getTime() - offset * 60000)
  return local.toISOString().slice(0, 16)
}

export default function PostEditorModal({ isOpen, onClose, onSave, post, pages }: PostEditorModalProps) {
  const toast = useToast()

  const [selectedPageId, setSelectedPageId] = useState('')
  const [contentText, setContentText] = useState('')
  const [scheduledAt, setScheduledAt] = useState('')
  const [imageKey, setImageKey] = useState<string | null>(null)
  const [imageUrl, setImageUrl] = useState<string | null>(null)
  const [linkUrl, setLinkUrl] = useState('')
  const [uploading, setUploading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [attempted, setAttempted] = useState(false)

  useEffect(() => {
    if (!isOpen) return
    if (post) {
      setSelectedPageId(post.page_id)
      setContentText(post.content_text)
      setScheduledAt(toLocalDatetime(post.scheduled_at))
      setImageKey(post.image_key ?? null)
      setImageUrl(post.image_url ?? null)
      setLinkUrl(post.link_url ?? '')
    } else {
      setSelectedPageId(pages[0]?.id ?? '')
      setContentText('')
      setScheduledAt('')
      setImageKey(null)
      setImageUrl(null)
      setLinkUrl('')
    }
    setAttempted(false)
    setSaving(false)
    setUploading(false)
  }, [isOpen, post, pages])

  async function handleImageUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file || !selectedPageId) return
    setUploading(true)
    try {
      const result = await uploadImage(file, selectedPageId)
      setImageKey(result.image_key)
      setImageUrl(result.url)
    } catch {
      toast.error('Failed to upload image')
    } finally {
      setUploading(false)
    }
  }

  async function handleSave(status: 'draft' | 'queued') {
    setAttempted(true)
    if (!selectedPageId || !contentText.trim()) return

    const scheduledIso = scheduledAt ? new Date(scheduledAt).toISOString() : undefined

    setSaving(true)
    try {
      if (post) {
        await updatePost(post.id, {
          content_text: contentText,
          image_key: imageKey ?? undefined,
          link_url: linkUrl || undefined,
          status,
          scheduled_at: scheduledIso,
        })
        toast.success('Post updated')
      } else {
        const created = await createPost({
          page_id: selectedPageId,
          content_text: contentText,
          image_key: imageKey ?? undefined,
          link_url: linkUrl || undefined,
          scheduled_at: scheduledIso,
        })
        if (status === 'queued') {
          await updatePost(created.id, { status: 'queued' })
        }
        toast.success(scheduledIso ? 'Post scheduled' : 'Post created')
      }
      onSave()
    } catch {
      toast.error('Failed to save post')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={post ? 'Edit Post' : 'New Post'}
      footer={
        <>
          <button
            onClick={() => handleSave('draft')}
            disabled={saving}
            className="px-4 py-2 text-sm border rounded-lg hover:bg-gray-50 disabled:opacity-50"
          >
            Save as Draft
          </button>
          <button
            onClick={() => handleSave('queued')}
            disabled={saving}
            className="px-4 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            {scheduledAt ? 'Schedule' : 'Save as Queued'}
          </button>
        </>
      }
    >
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Channel</label>
          <select
            value={selectedPageId}
            onChange={(e) => setSelectedPageId(e.target.value)}
            disabled={!!post}
            className={`w-full border rounded-lg px-3 py-2 text-sm ${
              attempted && !selectedPageId ? 'border-red-500' : ''
            }`}
          >
            <option value="">Select channel...</option>
            {pages.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Content</label>
          <textarea
            value={contentText}
            onChange={(e) => setContentText(e.target.value)}
            rows={4}
            placeholder="Write your post content..."
            className={`w-full border rounded-lg px-3 py-2 text-sm resize-none ${
              attempted && !contentText.trim() ? 'border-red-500' : ''
            }`}
          />
          <p className="text-xs text-gray-400 mt-1">{contentText.length} characters</p>
        </div>

        <SchedulePicker value={scheduledAt} onChange={setScheduledAt} />

        <div>
          <label className="block text-sm font-medium mb-1">Image</label>
          <label className={`inline-flex items-center gap-2 px-4 py-2 text-sm border rounded-lg cursor-pointer hover:bg-gray-50 ${uploading ? 'opacity-50 pointer-events-none' : ''}`}>
            <span>{uploading ? 'Uploading...' : 'Choose file'}</span>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              disabled={uploading}
              className="hidden"
            />
          </label>
          {imageUrl && (
            <div className="mt-2">
              <img src={imageUrl} alt="Preview" className="max-h-32 rounded" />
              <button
                onClick={() => { setImageKey(null); setImageUrl(null) }}
                className="text-xs text-red-500 mt-1"
              >
                Remove image
              </button>
            </div>
          )}
        </div>

        {!imageKey && (
          <div>
            <label className="block text-sm font-medium mb-1">Link URL</label>
            <input
              type="url"
              value={linkUrl}
              onChange={(e) => setLinkUrl(e.target.value)}
              placeholder="https://..."
              className="w-full border rounded-lg px-3 py-2 text-sm"
            />
          </div>
        )}
      </div>
    </Modal>
  )
}
