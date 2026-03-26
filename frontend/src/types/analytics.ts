export interface PostEngagement {
  post_id: string
  content_preview: string
  page_name: string
  likes: number
  comments: number
  shares: number
  published_at?: string
}

export interface HeatmapCell {
  day: number
  hour: number
  avg_engagement: number
}
