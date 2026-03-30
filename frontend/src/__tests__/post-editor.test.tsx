import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import PostEditorModal from '../components/ContentQueue/PostEditorModal'
import BulkImportModal from '../components/ContentQueue/BulkImportModal'
import { ToastProvider } from '../components/shared/Toast'
import type { Page } from '../types/page'
import type { Post } from '../types/post'

vi.mock('../api/posts', () => ({
  createPost: vi.fn().mockResolvedValue({ id: 'new' }),
  updatePost: vi.fn().mockResolvedValue({ id: 'existing' }),
  bulkImport: vi.fn().mockResolvedValue({ task_id: 'task-1' }),
}))

vi.mock('../api/images', () => ({
  uploadImage: vi.fn().mockResolvedValue({ image_key: 'key', url: 'http://img.jpg' }),
}))

const pages: Page[] = [
  { id: 'p1', fb_page_id: 'fb1', name: 'Page One', token_status: 'configured', queued_count: 0 },
  { id: 'p2', fb_page_id: 'fb2', name: 'Page Two', token_status: 'configured', queued_count: 0 },
]

function wrap(ui: React.ReactElement) {
  return render(<MemoryRouter><ToastProvider>{ui}</ToastProvider></MemoryRouter>)
}

describe('PostEditorModal', () => {
  const noop = () => {}

  it('renders form fields when open in create mode', () => {
    wrap(<PostEditorModal isOpen={true} onClose={noop} onSave={noop} post={null} pages={pages} />)
    expect(screen.getByText('New Post')).toBeDefined()
    expect(screen.getByPlaceholderText('Write your post content...')).toBeDefined()
  })

  it('pre-fills content_text when in edit mode', () => {
    const post: Post = {
      id: 'e1', page_id: 'p1', content_text: 'Existing content',
      post_type: 'text', status: 'draft',
    }
    wrap(<PostEditorModal isOpen={true} onClose={noop} onSave={noop} post={post} pages={pages} />)
    expect(screen.getByText('Edit Post')).toBeDefined()
    const textarea = screen.getByPlaceholderText('Write your post content...') as HTMLTextAreaElement
    expect(textarea.value).toBe('Existing content')
  })

  it('calls onSave after successful create', async () => {
    const { createPost } = await import('../api/posts')
    const onSave = vi.fn()
    wrap(<PostEditorModal isOpen={true} onClose={noop} onSave={onSave} post={null} pages={pages} />)

    const textarea = screen.getByPlaceholderText('Write your post content...')
    fireEvent.change(textarea, { target: { value: 'New post content' } })
    fireEvent.click(screen.getByText('Save as Queued'))

    await waitFor(() => {
      expect(createPost).toHaveBeenCalled()
      expect(onSave).toHaveBeenCalled()
    })
  })
})

describe('BulkImportModal', () => {
  const noop = () => {}

  it('renders file input when open', () => {
    wrap(<BulkImportModal isOpen={true} onClose={noop} onImported={noop} />)
    expect(screen.getByText('Bulk Import')).toBeDefined()
  })

  it('disables Import button when no file selected', () => {
    wrap(<BulkImportModal isOpen={true} onClose={noop} onImported={noop} />)
    const btn = screen.getByText('Import') as HTMLButtonElement
    expect(btn.disabled).toBe(true)
  })

  it('calls onImported after successful upload', async () => {
    const { bulkImport } = await import('../api/posts')
    const onImported = vi.fn()
    wrap(<BulkImportModal isOpen={true} onClose={noop} onImported={onImported} />)

    const file = new File(['test'], 'posts.csv', { type: 'text/csv' })
    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    fireEvent.change(input, { target: { files: [file] } })
    fireEvent.click(screen.getByText('Import'))

    await waitFor(() => {
      expect(bulkImport).toHaveBeenCalled()
      expect(onImported).toHaveBeenCalled()
    })
  })
})
