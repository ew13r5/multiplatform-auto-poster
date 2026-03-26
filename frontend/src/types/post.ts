export type PostStatus = 'draft' | 'queued' | 'publishing' | 'published' | 'failed'
export type PostType = 'text' | 'photo' | 'link'

export interface Post {
  id: string
  page_id: string
  content_text: string
  post_type: PostType
  status: PostStatus
  order_index?: number
  image_key?: string
  image_url?: string
  link_url?: string
  fb_post_id?: string
  created_at?: string
  updated_at?: string
}

export interface PostCreate {
  page_id: string
  content_text: string
  image_key?: string
  link_url?: string
}

export interface PostUpdate {
  content_text?: string
  image_key?: string
  link_url?: string
  status?: 'draft' | 'queued'
}
