import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../api/health', () => ({
  getHealth: vi.fn(),
  getLog: vi.fn(),
}))
vi.mock('../api/pages', () => ({
  getPages: vi.fn(),
}))
vi.mock('../hooks/useWebSocket', () => ({
  useWebSocket: () => ({ lastEvent: null, isConnected: true }),
}))

import { getHealth, getLog } from '../api/health'
import { getPages } from '../api/pages'
import Dashboard from '../pages/Dashboard'

const mockHealth = {
  status: 'healthy',
  checks: { db: true, redis: true, minio: false },
  mode: 'development',
}

const mockPages = [
  { id: '1', fb_page_id: 'fb1', name: 'Page One', category: 'Tech', token_status: 'configured' as const, queued_count: 3, last_published_at: new Date().toISOString() },
  { id: '2', fb_page_id: 'fb2', name: 'Page Two', category: undefined, token_status: 'missing' as const, queued_count: 5, last_published_at: undefined },
]

const mockLog = {
  entries: [
    { attempted_at: new Date().toISOString(), page_name: 'Page One', content_preview: 'Hello world post', result: 'success', retry_count: 0 },
    { attempted_at: new Date().toISOString(), page_name: 'Page Two', content_preview: 'Another post', result: 'success', retry_count: 0 },
    { attempted_at: new Date().toISOString(), page_name: 'Page One', content_preview: 'Failed post', result: 'permanent_error', error_message: 'Token expired', retry_count: 3 },
  ],
  total: 3,
}

function renderDashboard() {
  return render(
    <MemoryRouter>
      <Dashboard />
    </MemoryRouter>
  )
}

describe('Dashboard', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('shows loading spinner while loading', () => {
    vi.mocked(getHealth).mockReturnValue(new Promise(() => {}))
    vi.mocked(getPages).mockReturnValue(new Promise(() => {}))
    vi.mocked(getLog).mockReturnValue(new Promise(() => {}))

    renderDashboard()
    expect(screen.getByLabelText('Loading')).toBeInTheDocument()
  })

  it('shows error state on fetch error', async () => {
    vi.mocked(getHealth).mockRejectedValue(new Error('Network error'))
    vi.mocked(getPages).mockResolvedValue([])
    vi.mocked(getLog).mockResolvedValue({ entries: [], total: 0 })

    renderDashboard()
    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument()
    })
    expect(screen.getByText('Retry')).toBeInTheDocument()
  })

  it('renders Quick Stats with correct numbers', async () => {
    vi.mocked(getHealth).mockResolvedValue(mockHealth)
    vi.mocked(getPages).mockResolvedValue(mockPages)
    vi.mocked(getLog).mockResolvedValue(mockLog)

    renderDashboard()
    await waitFor(() => {
      expect(screen.getByText('Total Pages')).toBeInTheDocument()
    })
    expect(screen.getByText('Queued Posts')).toBeInTheDocument()
    expect(screen.getByText('Published Today')).toBeInTheDocument()
    expect(screen.getByText('Failed Today')).toBeInTheDocument()
    expect(screen.getByText('8')).toBeInTheDocument() // queued (3+5)
  })

  it('renders System Health with service indicators', async () => {
    vi.mocked(getHealth).mockResolvedValue(mockHealth)
    vi.mocked(getPages).mockResolvedValue(mockPages)
    vi.mocked(getLog).mockResolvedValue(mockLog)

    renderDashboard()
    await waitFor(() => {
      expect(screen.getByText('System Health')).toBeInTheDocument()
    })
    expect(screen.getByText('db')).toBeInTheDocument()
    expect(screen.getByText('minio')).toBeInTheDocument()
  })

  it('renders Connected Pages list', async () => {
    vi.mocked(getHealth).mockResolvedValue(mockHealth)
    vi.mocked(getPages).mockResolvedValue(mockPages)
    vi.mocked(getLog).mockResolvedValue(mockLog)

    renderDashboard()
    await waitFor(() => {
      expect(screen.getByText('Connected Pages')).toBeInTheDocument()
    })
    expect(screen.getAllByText('Page One').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Page Two').length).toBeGreaterThan(0)
  })

  it('shows empty state when no pages', async () => {
    vi.mocked(getHealth).mockResolvedValue(mockHealth)
    vi.mocked(getPages).mockResolvedValue([])
    vi.mocked(getLog).mockResolvedValue({ entries: [], total: 0 })

    renderDashboard()
    await waitFor(() => {
      expect(screen.getByText('No pages connected')).toBeInTheDocument()
    })
  })

  it('renders Recent Activity', async () => {
    vi.mocked(getHealth).mockResolvedValue(mockHealth)
    vi.mocked(getPages).mockResolvedValue(mockPages)
    vi.mocked(getLog).mockResolvedValue(mockLog)

    renderDashboard()
    await waitFor(() => {
      expect(screen.getByText('Recent Activity')).toBeInTheDocument()
    })
    expect(screen.getByText('Hello world post')).toBeInTheDocument()
  })

  it('shows empty state when no log entries', async () => {
    vi.mocked(getHealth).mockResolvedValue(mockHealth)
    vi.mocked(getPages).mockResolvedValue(mockPages)
    vi.mocked(getLog).mockResolvedValue({ entries: [], total: 0 })

    renderDashboard()
    await waitFor(() => {
      expect(screen.getByText('No publishing activity yet')).toBeInTheDocument()
    })
  })
})
