import { useEffect, useState } from 'react'
import type { AlertConfig, AlertConfigUpdate } from '../../api/alerts'
import { getAlertConfigs, updateAlertConfig } from '../../api/alerts'
import { useToast } from '../shared/Toast'
import LoadingSpinner from '../shared/LoadingSpinner'

export default function AlertConfigPanel() {
  const toast = useToast()
  const [configs, setConfigs] = useState<AlertConfig[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState<string | null>(null)

  useEffect(() => {
    getAlertConfigs()
      .then(setConfigs)
      .catch(() => toast.error('Failed to load alert config'))
      .finally(() => setLoading(false))
  }, [])

  async function handleSave(config: AlertConfig) {
    setSaving(config.page_id)
    try {
      const update: AlertConfigUpdate = {
        page_id: config.page_id,
        telegram_enabled: config.telegram_enabled,
        telegram_chat_ids: config.telegram_chat_ids,
        email_enabled: config.email_enabled,
        email_recipients: config.email_recipients,
        dedup_window_minutes: config.dedup_window_minutes,
      }
      await updateAlertConfig(update)
      toast.success('Alert config saved')
    } catch {
      toast.error('Failed to save alert config')
    } finally {
      setSaving(null)
    }
  }

  function updateConfig(pageId: string, changes: Partial<AlertConfig>) {
    setConfigs((prev) =>
      prev.map((c) => (c.page_id === pageId ? { ...c, ...changes } : c)),
    )
  }

  if (loading) return <LoadingSpinner size="sm" />

  if (configs.length === 0) {
    return <p className="text-sm text-gray-500">Connect a page first to configure alerts.</p>
  }

  return (
    <div className="space-y-6">
      {configs.map((config) => (
        <div key={config.page_id} className="border rounded-lg p-4 space-y-3">
          <h4 className="font-medium text-sm">{config.page_name}</h4>

          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={config.telegram_enabled}
                onChange={(e) => updateConfig(config.page_id, { telegram_enabled: e.target.checked })}
              />
              Telegram
            </label>
            {config.telegram_enabled && (
              <input
                type="text"
                value={config.telegram_chat_ids.join(', ')}
                onChange={(e) =>
                  updateConfig(config.page_id, {
                    telegram_chat_ids: e.target.value.split(',').map((s) => s.trim()).filter(Boolean),
                  })
                }
                placeholder="Chat IDs (comma-separated)"
                className="flex-1 border rounded px-2 py-1 text-sm"
              />
            )}
          </div>

          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={config.email_enabled}
                onChange={(e) => updateConfig(config.page_id, { email_enabled: e.target.checked })}
              />
              Email
            </label>
            {config.email_enabled && (
              <input
                type="text"
                value={config.email_recipients.join(', ')}
                onChange={(e) =>
                  updateConfig(config.page_id, {
                    email_recipients: e.target.value.split(',').map((s) => s.trim()).filter(Boolean),
                  })
                }
                placeholder="Recipients (comma-separated)"
                className="flex-1 border rounded px-2 py-1 text-sm"
              />
            )}
          </div>

          <div className="flex items-center gap-3">
            <label className="text-sm">Dedup window (min):</label>
            <input
              type="number"
              value={config.dedup_window_minutes}
              onChange={(e) =>
                updateConfig(config.page_id, { dedup_window_minutes: parseInt(e.target.value) || 30 })
              }
              className="w-20 border rounded px-2 py-1 text-sm"
              min={1}
            />
          </div>

          <button
            onClick={() => handleSave(config)}
            disabled={saving === config.page_id}
            className="px-3 py-1.5 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            {saving === config.page_id ? 'Saving...' : 'Save'}
          </button>
        </div>
      ))}
    </div>
  )
}
