import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Queue from '../pages/Queue'
import { ToastProvider } from '../components/shared/Toast'

vi.mock('../api/posts', () => ({
  getPosts: vi.fn().mockResolvedValue({
    posts: [
      { id: '1', page_id: 'p1', content_text: 'First post', post_type: 'text', status: 'draft' },
      { id: '2', page_id: 'p1', content_text: 'Second post', post_type: 'text', status: 'queued' },
    ],
    total: 2,
  }),
  deletePost: vi.fn().mockResolvedValue(undefined),
  publishNow: vi.fn().mockResolvedValue(undefined),
  reorderPosts: vi.fn().mockResolvedValue(undefined),
  createPost: vi.fn().mockResolvedValue({ id: 'new' }),
  updatePost: vi.fn().mockResolvedValue({ id: '1' }),
  bulkImport: vi.fn().mockResolvedValue({ task_id: 't1' }),
}))

vi.mock('../api/pages', () => ({
  getPages: vi.fn().mockResolvedValue([
    { id: 'p1', fb_page_id: 'fb1', name: 'Test Page', token_status: 'configured', queued_count: 1 },
  ]),
}))

vi.mock('../api/images', () => ({
  uploadImage: vi.fn().mockResolvedValue({ image_key: 'k', url: 'http://img.jpg' }),
}))

function renderQueue() {
  return render(
    <MemoryRouter>
      <ToastProvider>
        <Queue />
      </ToastProvider>
    </MemoryRouter>
  )
}

describe('Queue Page', () => {
  it('renders posts after fetch', async () => {
    renderQueue()
    await waitFor(() => {
      expect(screen.getByText('First post')).toBeDefined()
      expect(screen.getByText('Second post')).toBeDefined()
    })
  })

  it('renders Content Queue heading', async () => {
    renderQueue()
    await waitFor(() => {
      expect(screen.getByText('Content Queue')).toBeDefined()
    })
  })

  it('opens PostEditorModal on + New Post click', async () => {
    renderQueue()
    await waitFor(() => screen.getByText('Content Queue'))
    fireEvent.click(screen.getByText('+ New Post'))
    await waitFor(() => {
      expect(screen.getByText('New Post', { selector: 'h2' })).toBeDefined()
    })
  })

  it('shows timeline and list toggle', async () => {
    renderQueue()
    await waitFor(() => {
      expect(screen.getByText('Timeline')).toBeDefined()
      expect(screen.getByText('List')).toBeDefined()
    })
  })

  it('filters posts when status tab clicked', async () => {
    const { getPosts } = await import('../api/posts')
    renderQueue()
    await waitFor(() => screen.getByText('Content Queue'))

    vi.mocked(getPosts).mockClear()
    // Use getAllByText since "Draft" appears in both tab and status badge
    const draftButtons = screen.getAllByText('Draft')
    fireEvent.click(draftButtons[0])

    await waitFor(() => {
      expect(getPosts).toHaveBeenCalledWith(expect.objectContaining({ status: 'draft' }))
    })
  })
})
