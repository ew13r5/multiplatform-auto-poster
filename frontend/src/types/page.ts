export interface Page {
  id: string
  fb_page_id: string
  name: string
  category?: string
  token_status: 'configured' | 'missing'
  queued_count: number
  last_published_at?: string
  created_at?: string
}

export interface PageConnect {
  fb_page_id: string
  name: string
  access_token: string
  category?: string
}
