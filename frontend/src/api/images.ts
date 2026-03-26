import apiClient from './client'

export async function uploadImage(file: File, pageId: string) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await apiClient.post(`/images/upload?page_id=${pageId}`, formData)
  return data as { image_key: string; url: string }
}
