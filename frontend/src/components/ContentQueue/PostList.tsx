import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core'
import type { DragEndEvent } from '@dnd-kit/core'
import {
  SortableContext,
  verticalListSortingStrategy,
  arrayMove,
  useSortable,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { sortableKeyboardCoordinates } from '@dnd-kit/sortable'
import { ListTodo } from 'lucide-react'
import type { Post } from '../../types/post'
import PostRow from './PostRow'
import EmptyState from '../shared/EmptyState'

interface PostListProps {
  posts: Post[]
  pageMap: Map<string, string>
  onEdit: (post: Post) => void
  onDelete: (id: string) => void
  onPublish: (id: string) => void
  onRetry?: (id: string) => void
  onReorder: (items: { id: string; order_index: number }[]) => void
}

function SortablePostRow({
  post,
  pageName,
  onEdit,
  onDelete,
  onPublish,
  onRetry,
  isDraggable,
}: {
  post: Post
  pageName?: string
  onEdit: (post: Post) => void
  onDelete: (id: string) => void
  onPublish: (id: string) => void
  onRetry?: (id: string) => void
  isDraggable: boolean
}) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: post.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  return (
    <div ref={setNodeRef} style={style}>
      <PostRow
        post={post}
        pageName={pageName}
        onEdit={onEdit}
        onDelete={onDelete}
        onPublish={onPublish}
        onRetry={onRetry}
        dragHandleProps={isDraggable ? { ...attributes, ...listeners } : undefined}
      />
    </div>
  )
}

export default function PostList({ posts, pageMap, onEdit, onDelete, onPublish, onRetry, onReorder }: PostListProps) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )

  if (posts.length === 0) {
    return <EmptyState icon={ListTodo} title="No posts" description="Create your first post" />
  }

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event
    if (!over || active.id === over.id) return

    const oldIndex = posts.findIndex((p) => p.id === active.id)
    const newIndex = posts.findIndex((p) => p.id === over.id)
    if (oldIndex === -1 || newIndex === -1) return

    const reordered = arrayMove(posts, oldIndex, newIndex)
    const items = reordered.map((p, i) => ({ id: p.id, order_index: i * 10 }))
    onReorder(items)
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={posts.map((p) => p.id)} strategy={verticalListSortingStrategy}>
        {posts.map((post) => (
          <SortablePostRow
            key={post.id}
            post={post}
            pageName={pageMap.get(post.page_id)}
            onEdit={onEdit}
            onDelete={onDelete}
            onPublish={onPublish}
            onRetry={onRetry}
            isDraggable={post.status === 'queued'}
          />
        ))}
      </SortableContext>
    </DndContext>
  )
}
