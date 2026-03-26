import apiClient from './client'
import type { Page, PageConnect } from '../types/page'

export async function getPages(): Promise<Page[]> {
  const { data } = await apiClient.get('/pages')
  return data.pages
}

export async function connectPage(payload: PageConnect): Promise<Page> {
  const { data } = await apiClient.post('/pages/connect', payload)
  return data
}

export async function verifyToken(pageId: string) {
  const { data } = await apiClient.post(`/pages/${pageId}/verify-token`)
  return data
}
