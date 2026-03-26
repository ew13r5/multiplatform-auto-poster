import apiClient from './client'
import type { LogResponse } from '../types/log'

export async function getHealth() {
  const { data } = await apiClient.get('/health')
  return data as { status: string; checks: Record<string, boolean>; mode: string }
}

export async function getLog(params?: { page_id?: string; status?: string; limit?: number; offset?: number }) {
  const { data } = await apiClient.get('/log', { params })
  return data as LogResponse
}

export async function getTaskStatus(taskId: string) {
  const { data } = await apiClient.get(`/tasks/${taskId}`)
  return data as { task_id: string; status: string; result: unknown }
}
