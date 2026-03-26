import apiClient from './client'
import type { ScheduleSlot } from '../types/schedule'

export async function getSchedule() {
  const { data } = await apiClient.get('/schedule')
  return data.slots as ScheduleSlot[]
}

export async function updateSchedule(slots: ScheduleSlot[]) {
  await apiClient.put('/schedule', { slots })
}

export async function togglePause(paused: boolean) {
  const { data } = await apiClient.post('/schedule/pause', { paused })
  return data as { paused: boolean }
}
