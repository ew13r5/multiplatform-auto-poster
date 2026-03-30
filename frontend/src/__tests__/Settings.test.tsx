import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Settings from '../pages/Settings'
import { ToastProvider } from '../components/shared/Toast'

vi.mock('../api/pages', () => ({
  getPages: vi.fn().mockResolvedValue([
    { id: 'p1', fb_page_id: 'fb1', name: 'Test Page', token_status: 'configured', queued_count: 0 },
  ]),
  connectPage: vi.fn().mockResolvedValue({ id: 'p2' }),
  verifyToken: vi.fn().mockResolvedValue({ valid: true }),
}))

vi.mock('../api/alerts', () => ({
  getAlertConfigs: vi.fn().mockResolvedValue([
    {
      page_id: 'p1', page_name: 'Test Page',
      telegram_enabled: false, telegram_chat_ids: [],
      email_enabled: false, email_recipients: [],
      dedup_window_minutes: 30,
    },
  ]),
  updateAlertConfig: vi.fn().mockResolvedValue(undefined),
}))

vi.mock('../api/health', () => ({
  getLog: vi.fn().mockResolvedValue({ entries: [], total: 0 }),
  getHealth: vi.fn().mockResolvedValue({ status: 'ok', checks: {}, mode: 'live' }),
  getTaskStatus: vi.fn().mockResolvedValue({ task_id: 't1', status: 'SUCCESS', result: null }),
}))

function renderSettings() {
  return render(
    <MemoryRouter>
      <ToastProvider>
        <Settings />
      </ToastProvider>
    </MemoryRouter>
  )
}

describe('Settings Page', () => {
  it('renders all sections after fetch', async () => {
    renderSettings()
    await waitFor(() => {
      expect(screen.getByText('Settings')).toBeDefined()
      expect(screen.getByText('Connect Channel')).toBeDefined()
      expect(screen.getByText('Connected Pages')).toBeDefined()
      expect(screen.getByText('Alert Configuration')).toBeDefined()
      expect(screen.getByText('Publishing Log')).toBeDefined()
    })
  })

  it('shows connected page name', async () => {
    renderSettings()
    await waitFor(() => {
      expect(screen.getAllByText('Test Page').length).toBeGreaterThanOrEqual(1)
    })
  })

  it('shows connect form with platform selector', async () => {
    renderSettings()
    await waitFor(() => {
      expect(screen.getByText('Platform')).toBeDefined()
      expect(screen.getByText('Telegram')).toBeDefined()
      expect(screen.getByText('X / Twitter')).toBeDefined()
      expect(screen.getByPlaceholderText('My Channel')).toBeDefined()
    })
  })
})
