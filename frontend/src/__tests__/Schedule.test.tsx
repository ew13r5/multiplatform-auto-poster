import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Schedule from '../pages/Schedule'
import { ToastProvider } from '../components/shared/Toast'

vi.mock('../api/schedule', () => ({
  getSchedule: vi.fn().mockResolvedValue([]),
  updateSchedule: vi.fn().mockResolvedValue(undefined),
  togglePause: vi.fn().mockResolvedValue({ paused: true }),
}))

vi.mock('../api/posts', () => ({
  getPosts: vi.fn().mockResolvedValue({ posts: [], total: 0 }),
  createPost: vi.fn().mockResolvedValue({ id: 'new' }),
  updatePost: vi.fn().mockResolvedValue({ id: '1' }),
}))

vi.mock('../api/pages', () => ({
  getPages: vi.fn().mockResolvedValue([
    { id: 'p1', fb_page_id: 'fb1', name: 'Test Page', token_status: 'configured', queued_count: 0 },
  ]),
}))

vi.mock('../api/images', () => ({
  uploadImage: vi.fn().mockResolvedValue({ image_key: 'k', url: 'http://img.jpg' }),
}))

function renderSchedule() {
  return render(
    <MemoryRouter>
      <ToastProvider>
        <Schedule />
      </ToastProvider>
    </MemoryRouter>
  )
}

describe('Schedule Page', () => {
  it('renders week calendar after fetch', async () => {
    renderSchedule()
    await waitFor(() => {
      expect(screen.getByText('Schedule')).toBeDefined()
      expect(screen.getByText('Mon')).toBeDefined()
      expect(screen.getByText('Today')).toBeDefined()
    })
  })

  it('shows pause button', async () => {
    renderSchedule()
    await waitFor(() => {
      expect(screen.getByText('Pause')).toBeDefined()
    })
  })
})
