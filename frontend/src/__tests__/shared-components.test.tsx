import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { Globe } from 'lucide-react'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import ErrorState from '../components/shared/ErrorState'
import EmptyState from '../components/shared/EmptyState'
import Card from '../components/shared/Card'

describe('LoadingSpinner', () => {
  it('renders without crashing', () => {
    render(<LoadingSpinner />)
    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  it('renders with size="sm"', () => {
    render(<LoadingSpinner size="sm" />)
    const spinner = screen.getByRole('status')
    expect(spinner.className).toContain('w-4')
    expect(spinner.className).toContain('h-4')
  })

  it('has aria-label="Loading"', () => {
    render(<LoadingSpinner />)
    expect(screen.getByLabelText('Loading')).toBeInTheDocument()
  })
})

describe('ErrorState', () => {
  it('renders error message text', () => {
    render(<ErrorState message="Something broke" />)
    expect(screen.getByText('Something broke')).toBeInTheDocument()
  })

  it('renders retry button when onRetry provided', () => {
    render(<ErrorState message="Error" onRetry={() => {}} />)
    expect(screen.getByText('Retry')).toBeInTheDocument()
  })

  it('hides retry button when no onRetry', () => {
    render(<ErrorState message="Error" />)
    expect(screen.queryByText('Retry')).not.toBeInTheDocument()
  })

  it('calls onRetry callback when button clicked', () => {
    const onRetry = vi.fn()
    render(<ErrorState message="Error" onRetry={onRetry} />)
    fireEvent.click(screen.getByText('Retry'))
    expect(onRetry).toHaveBeenCalledOnce()
  })
})

describe('EmptyState', () => {
  it('renders title and description', () => {
    render(<EmptyState icon={Globe} title="No items" description="Nothing here" />)
    expect(screen.getByText('No items')).toBeInTheDocument()
    expect(screen.getByText('Nothing here')).toBeInTheDocument()
  })

  it('renders icon as SVG', () => {
    const { container } = render(<EmptyState icon={Globe} title="Test" description="Test" />)
    expect(container.querySelector('svg')).toBeInTheDocument()
  })

  it('renders action button when provided', () => {
    render(
      <EmptyState
        icon={Globe}
        title="Test"
        description="Test"
        action={{ label: 'Add Item', onClick: () => {} }}
      />
    )
    expect(screen.getByText('Add Item')).toBeInTheDocument()
  })

  it('calls action.onClick when button clicked', () => {
    const onClick = vi.fn()
    render(
      <EmptyState
        icon={Globe}
        title="Test"
        description="Test"
        action={{ label: 'Add', onClick }}
      />
    )
    fireEvent.click(screen.getByText('Add'))
    expect(onClick).toHaveBeenCalledOnce()
  })

  it('no action button when not provided', () => {
    render(<EmptyState icon={Globe} title="Test" description="Test" />)
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })
})

describe('Card', () => {
  it('renders children content', () => {
    render(<Card><p>Hello</p></Card>)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })

  it('renders title in header', () => {
    render(<Card title="My Card"><p>Content</p></Card>)
    expect(screen.getByText('My Card')).toBeInTheDocument()
  })

  it('renders headerAction', () => {
    render(<Card headerAction={<button>Click</button>}><p>Content</p></Card>)
    expect(screen.getByText('Click')).toBeInTheDocument()
  })

  it('no header when no title and no headerAction', () => {
    const { container } = render(<Card><p>Content</p></Card>)
    expect(container.querySelector('h2')).not.toBeInTheDocument()
  })
})
