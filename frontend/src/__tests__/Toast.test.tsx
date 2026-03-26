import { render, screen, fireEvent, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ToastProvider, useToast } from '../components/shared/Toast'

function TestComponent() {
  const toast = useToast()
  return (
    <div>
      <button onClick={() => toast.success('Success!')}>Show Success</button>
      <button onClick={() => toast.error('Error!')}>Show Error</button>
    </div>
  )
}

function renderWithProvider() {
  return render(
    <ToastProvider>
      <TestComponent />
    </ToastProvider>
  )
}

describe('Toast System', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('success() adds success toast to DOM', () => {
    renderWithProvider()
    fireEvent.click(screen.getByText('Show Success'))
    expect(screen.getByText('Success!')).toBeInTheDocument()
  })

  it('error() adds error toast to DOM', () => {
    renderWithProvider()
    fireEvent.click(screen.getByText('Show Error'))
    expect(screen.getByText('Error!')).toBeInTheDocument()
  })

  it('auto-dismisses after 5 seconds', () => {
    renderWithProvider()
    fireEvent.click(screen.getByText('Show Success'))
    expect(screen.getByText('Success!')).toBeInTheDocument()
    act(() => { vi.advanceTimersByTime(5000) })
    expect(screen.queryByText('Success!')).not.toBeInTheDocument()
  })

  it('manual dismiss removes toast', () => {
    renderWithProvider()
    fireEvent.click(screen.getByText('Show Success'))
    expect(screen.getByText('Success!')).toBeInTheDocument()
    const closeButtons = screen.getAllByRole('button').filter(
      (btn) => btn.closest('[role="alert"]')
    )
    fireEvent.click(closeButtons[0])
    expect(screen.queryByText('Success!')).not.toBeInTheDocument()
  })

  it('multiple toasts stack', () => {
    renderWithProvider()
    fireEvent.click(screen.getByText('Show Success'))
    fireEvent.click(screen.getByText('Show Error'))
    expect(screen.getByText('Success!')).toBeInTheDocument()
    expect(screen.getByText('Error!')).toBeInTheDocument()
  })
})
