import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import Modal from '../components/shared/Modal'

describe('Modal', () => {
  it('renders children when isOpen=true', () => {
    render(<Modal isOpen={true} onClose={() => {}} title="Test">Hello</Modal>)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })

  it('does not render when isOpen=false', () => {
    render(<Modal isOpen={false} onClose={() => {}} title="Test">Hello</Modal>)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('calls onClose when ESC pressed', () => {
    const onClose = vi.fn()
    render(<Modal isOpen={true} onClose={onClose} title="Test">Content</Modal>)
    fireEvent.keyDown(document, { key: 'Escape' })
    expect(onClose).toHaveBeenCalledOnce()
  })

  it('calls onClose when backdrop clicked', () => {
    const onClose = vi.fn()
    const { container } = render(<Modal isOpen={true} onClose={onClose} title="Test">Content</Modal>)
    const backdrop = container.querySelector('.fixed')!
    fireEvent.click(backdrop)
    expect(onClose).toHaveBeenCalledOnce()
  })

  it('does not call onClose when dialog body clicked', () => {
    const onClose = vi.fn()
    render(<Modal isOpen={true} onClose={onClose} title="Test">Content</Modal>)
    fireEvent.click(screen.getByText('Content'))
    expect(onClose).not.toHaveBeenCalled()
  })

  it('has role="dialog" and aria-modal="true"', () => {
    render(<Modal isOpen={true} onClose={() => {}} title="Test">Content</Modal>)
    const dialog = screen.getByRole('dialog')
    expect(dialog).toHaveAttribute('aria-modal', 'true')
  })
})
