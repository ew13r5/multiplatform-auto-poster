import apiClient from './client'
import type { PostEngagement, HeatmapCell } from '../types/analytics'

export async function getEngagement(params?: { page_id?: string; days?: number; limit?: number }) {
  const { data } = await apiClient.get('/analytics/engagement', { params })
  return data.posts as PostEngagement[]
}

export async function getBestTime(params?: { page_id?: string }) {
  const { data } = await apiClient.get('/analytics/best-time', { params })
  return data.cells as HeatmapCell[]
}
