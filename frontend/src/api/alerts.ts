import apiClient from './client'

export interface AlertConfig {
  page_id: string
  page_name: string
  telegram_enabled: boolean
  telegram_chat_ids: string[]
  email_enabled: boolean
  email_recipients: string[]
  dedup_window_minutes: number
}

export interface AlertConfigUpdate {
  page_id: string
  telegram_enabled: boolean
  telegram_chat_ids: string[]
  email_enabled: boolean
  email_recipients: string[]
  dedup_window_minutes: number
}

export async function getAlertConfigs(): Promise<AlertConfig[]> {
  const { data } = await apiClient.get('/alerts/config')
  return data.configs
}

export async function updateAlertConfig(config: AlertConfigUpdate) {
  await apiClient.put('/alerts/config', config)
}
