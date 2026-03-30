import apiClient from './client'
import type { Post, PostCreate, PostUpdate } from '../types/post'

export async function getPosts(params?: { page_id?: string; status?: string; limit?: number; offset?: number }) {
  const { data } = await apiClient.get('/posts', { params })
  return data as { posts: Post[]; total: number }
}

export async function createPost(payload: PostCreate): Promise<Post> {
  const { data } = await apiClient.post('/posts', payload)
  return data
}

export async function updatePost(id: string, payload: PostUpdate): Promise<Post> {
  const { data } = await apiClient.put(`/posts/${id}`, payload)
  return data
}

export async function deletePost(id: string) {
  await apiClient.delete(`/posts/${id}`)
}

export async function reorderPosts(items: { id: string; order_index: number }[]) {
  await apiClient.put('/posts/reorder', { items })
}

export async function bulkImport(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await apiClient.post('/posts/bulk', formData)
  return data as { task_id: string }
}

export async function publishNow(id: string) {
  const { data } = await apiClient.post(`/posts/${id}/publish-now`)
  return data
}

export async function retryPost(id: string) {
  const { data } = await apiClient.post(`/posts/${id}/retry`)
  return data
}
