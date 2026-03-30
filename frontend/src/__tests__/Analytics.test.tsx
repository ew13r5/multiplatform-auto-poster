import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Analytics from '../pages/Analytics'
import { ToastProvider } from '../components/shared/Toast'

// Mock ResizeObserver for Recharts
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
globalThis.ResizeObserver = ResizeObserverMock as unknown as typeof ResizeObserver

vi.mock('../api/analytics', () => ({
  getEngagement: vi.fn().mockResolvedValue([
    { post_id: '1', content_preview: 'Test post', page_name: 'Page 1', likes: 10, comments: 5, shares: 2, published_at: '2025-01-15T12:00:00Z' },
  ]),
  getBestTime: vi.fn().mockResolvedValue([
    { day: 0, hour: 9, avg_engagement: 15 },
  ]),
}))

vi.mock('../api/pages', () => ({
  getPages: vi.fn().mockResolvedValue([
    { id: 'p1', fb_page_id: 'fb1', name: 'Page 1', token_status: 'configured', queued_count: 0 },
  ]),
}))

function renderAnalytics() {
  return render(
    <MemoryRouter>
      <ToastProvider>
        <Analytics />
      </ToastProvider>
    </MemoryRouter>
  )
}

describe('Analytics Page', () => {
  it('renders charts after fetch', async () => {
    renderAnalytics()
    await waitFor(() => {
      expect(screen.getByText('Analytics')).toBeDefined()
      expect(screen.getByText('Engagement')).toBeDefined()
      expect(screen.getByText('Best Posting Time')).toBeDefined()
      expect(screen.getByText('Top Posts')).toBeDefined()
    })
  })

  it('shows date range buttons', async () => {
    renderAnalytics()
    await waitFor(() => {
      expect(screen.getByText('7d')).toBeDefined()
      expect(screen.getByText('30d')).toBeDefined()
      expect(screen.getByText('90d')).toBeDefined()
    })
  })

  it('changes date range when button clicked', async () => {
    const { getEngagement } = await import('../api/analytics')
    renderAnalytics()
    await waitFor(() => screen.getByText('Analytics'))

    vi.mocked(getEngagement).mockClear()
    fireEvent.click(screen.getByText('7d'))

    await waitFor(() => {
      expect(getEngagement).toHaveBeenCalledWith(expect.objectContaining({ days: 7 }))
    })
  })
})
