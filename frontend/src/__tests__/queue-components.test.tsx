import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import StatusTabs from '../components/ContentQueue/StatusTabs'
import PostRow from '../components/ContentQueue/PostRow'
import PostList from '../components/ContentQueue/PostList'
import type { Post } from '../types/post'

function makePost(overrides: Partial<Post> = {}): Post {
  return {
    id: '1',
    page_id: 'p1',
    content_text: 'Hello world test post',
    post_type: 'text',
    status: 'draft',
    ...overrides,
  }
}

describe('StatusTabs', () => {
  it('renders all 5 tab labels', () => {
    render(<StatusTabs selected="" onChange={() => {}} />)
    expect(screen.getByText('All')).toBeDefined()
    expect(screen.getByText('Draft')).toBeDefined()
    expect(screen.getByText('Queued')).toBeDefined()
    expect(screen.getByText('Published')).toBeDefined()
    expect(screen.getByText('Failed')).toBeDefined()
  })

  it('calls onChange with empty string when All clicked', () => {
    const onChange = vi.fn()
    render(<StatusTabs selected="draft" onChange={onChange} />)
    fireEvent.click(screen.getByText('All'))
    expect(onChange).toHaveBeenCalledWith('')
  })

  it('calls onChange with draft when Draft clicked', () => {
    const onChange = vi.fn()
    render(<StatusTabs selected="" onChange={onChange} />)
    fireEvent.click(screen.getByText('Draft'))
    expect(onChange).toHaveBeenCalledWith('draft')
  })

  it('highlights active tab', () => {
    render(<StatusTabs selected="queued" onChange={() => {}} />)
    const queuedBtn = screen.getByText('Queued')
    expect(queuedBtn.className).toContain('border-blue-500')
  })
})

describe('PostRow', () => {
  const noop = () => {}

  it('renders content preview text', () => {
    render(<PostRow post={makePost()} pageName="Test Page" onEdit={noop} onDelete={noop} onPublish={noop} />)
    expect(screen.getByText('Hello world test post')).toBeDefined()
  })

  it('renders StatusBadge with post status', () => {
    render(<PostRow post={makePost({ status: 'queued' })} onEdit={noop} onDelete={noop} onPublish={noop} />)
    expect(screen.getByText('queued')).toBeDefined()
  })

  it('shows Edit+Delete for draft post', () => {
    render(<PostRow post={makePost({ status: 'draft' })} onEdit={noop} onDelete={noop} onPublish={noop} />)
    expect(screen.getByLabelText('Edit')).toBeDefined()
    expect(screen.getByLabelText('Delete')).toBeDefined()
    expect(screen.queryByLabelText('Publish now')).toBeNull()
  })

  it('shows Edit+Delete+Publish for queued post', () => {
    render(<PostRow post={makePost({ status: 'queued' })} onEdit={noop} onDelete={noop} onPublish={noop} />)
    expect(screen.getByLabelText('Edit')).toBeDefined()
    expect(screen.getByLabelText('Delete')).toBeDefined()
    expect(screen.getByLabelText('Publish now')).toBeDefined()
  })

  it('shows no actions for published post', () => {
    render(<PostRow post={makePost({ status: 'published' })} onEdit={noop} onDelete={noop} onPublish={noop} />)
    expect(screen.queryByLabelText('Edit')).toBeNull()
    expect(screen.queryByLabelText('Delete')).toBeNull()
  })

  it('calls onEdit with post when Edit clicked', () => {
    const onEdit = vi.fn()
    const post = makePost()
    render(<PostRow post={post} onEdit={onEdit} onDelete={noop} onPublish={noop} />)
    fireEvent.click(screen.getByLabelText('Edit'))
    expect(onEdit).toHaveBeenCalledWith(post)
  })

  it('calls onDelete with post.id when Delete clicked', () => {
    const onDelete = vi.fn()
    render(<PostRow post={makePost({ id: 'abc' })} onEdit={noop} onDelete={onDelete} onPublish={noop} />)
    fireEvent.click(screen.getByLabelText('Delete'))
    expect(onDelete).toHaveBeenCalledWith('abc')
  })
})

describe('PostList', () => {
  const noop = () => {}

  it('renders PostRow for each post', () => {
    const posts = [
      makePost({ id: '1', content_text: 'Post one' }),
      makePost({ id: '2', content_text: 'Post two' }),
    ]
    render(
      <PostList posts={posts} pageMap={new Map()} onEdit={noop} onDelete={noop} onPublish={noop} onReorder={noop} />
    )
    expect(screen.getByText('Post one')).toBeDefined()
    expect(screen.getByText('Post two')).toBeDefined()
  })

  it('renders EmptyState when posts empty', () => {
    render(
      <PostList posts={[]} pageMap={new Map()} onEdit={noop} onDelete={noop} onPublish={noop} onReorder={noop} />
    )
    expect(screen.getByText('No posts')).toBeDefined()
  })
})
