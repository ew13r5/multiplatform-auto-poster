export interface PublishLogEntry {
  attempted_at: string
  page_name: string
  content_preview: string
  result: string
  fb_post_id?: string
  error_code?: number
  error_message?: string
  retry_count: number
}

export interface LogResponse {
  entries: PublishLogEntry[]
  total: number
}
