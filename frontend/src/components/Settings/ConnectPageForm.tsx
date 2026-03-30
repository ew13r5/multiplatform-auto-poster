import { useState } from 'react'
import type { Platform } from '../../types/page'
import { connectPage } from '../../api/pages'
import { useToast } from '../shared/Toast'

interface ConnectPageFormProps {
  onConnected: () => void
}

const platformConfig: Record<Platform, {
  idLabel: string
  idPlaceholder: string
  tokenLabel: string
  tokenPlaceholder: string
  isTwitter?: boolean
}> = {
  telegram: {
    idLabel: 'Chat ID',
    idPlaceholder: '@channel_name or -100...',
    tokenLabel: 'Bot Token',
    tokenPlaceholder: '123456:ABC-DEF...',
  },
  twitter: {
    idLabel: 'Username',
    idPlaceholder: '@yourhandle',
    tokenLabel: '',
    tokenPlaceholder: '',
    isTwitter: true,
  },
  facebook: {
    idLabel: 'Facebook Page ID',
    idPlaceholder: '123456789',
    tokenLabel: 'Access Token',
    tokenPlaceholder: 'EAA...',
  },
}

export default function ConnectPageForm({ onConnected }: ConnectPageFormProps) {
  const toast = useToast()
  const [platform, setPlatform] = useState<Platform>('telegram')
  const [fbPageId, setFbPageId] = useState('')
  const [name, setName] = useState('')
  const [accessToken, setAccessToken] = useState('')
  // Twitter-specific fields
  const [apiKey, setApiKey] = useState('')
  const [apiSecret, setApiSecret] = useState('')
  const [twAccessToken, setTwAccessToken] = useState('')
  const [twAccessSecret, setTwAccessSecret] = useState('')
  const [category, setCategory] = useState('')
  const [saving, setSaving] = useState(false)

  const config = platformConfig[platform]

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!fbPageId.trim() || !name.trim()) return

    if (platform === 'twitter') {
      if (!apiKey.trim() || !apiSecret.trim() || !twAccessToken.trim() || !twAccessSecret.trim()) return
    } else {
      if (!accessToken.trim()) return
    }

    setSaving(true)
    try {
      const token = platform === 'twitter'
        ? JSON.stringify({
            api_key: apiKey.trim(),
            api_secret: apiSecret.trim(),
            access_token: twAccessToken.trim(),
            access_token_secret: twAccessSecret.trim(),
          })
        : accessToken.trim()

      await connectPage({
        fb_page_id: fbPageId.trim(),
        name: name.trim(),
        access_token: token,
        category: category.trim() || undefined,
        platform,
      })
      toast.success('Channel connected')
      setFbPageId(''); setName(''); setAccessToken('')
      setApiKey(''); setApiSecret(''); setTwAccessToken(''); setTwAccessSecret('')
      setCategory('')
      onConnected()
    } catch {
      toast.error('Failed to connect')
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div>
        <label className="block text-sm font-medium mb-1">Platform</label>
        <div className="flex gap-2">
          {(['telegram', 'twitter', 'facebook'] as Platform[]).map((p) => (
            <button
              key={p}
              type="button"
              onClick={() => setPlatform(p)}
              className={`px-4 py-1.5 text-sm rounded-lg ${
                platform === p
                  ? p === 'twitter' ? 'bg-black text-white' : 'bg-blue-500 text-white'
                  : 'border hover:bg-gray-50'
              }`}
            >
              {p === 'twitter' ? 'X / Twitter' : p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium mb-1">{config.idLabel}</label>
          <input
            type="text"
            value={fbPageId}
            onChange={(e) => setFbPageId(e.target.value)}
            placeholder={config.idPlaceholder}
            className="w-full border rounded-lg px-3 py-2 text-sm"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Display Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="My Channel"
            className="w-full border rounded-lg px-3 py-2 text-sm"
            required
          />
        </div>
      </div>

      {config.isTwitter ? (
        <>
          <p className="text-xs text-gray-500">
            Get these from <strong>developer.x.com</strong> → Your App → Keys and Tokens
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">API Key</label>
              <input type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)}
                placeholder="Consumer API Key" className="w-full border rounded-lg px-3 py-2 text-sm" required />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">API Secret</label>
              <input type="password" value={apiSecret} onChange={(e) => setApiSecret(e.target.value)}
                placeholder="Consumer API Secret" className="w-full border rounded-lg px-3 py-2 text-sm" required />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Access Token</label>
              <input type="password" value={twAccessToken} onChange={(e) => setTwAccessToken(e.target.value)}
                placeholder="Access Token" className="w-full border rounded-lg px-3 py-2 text-sm" required />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Access Token Secret</label>
              <input type="password" value={twAccessSecret} onChange={(e) => setTwAccessSecret(e.target.value)}
                placeholder="Access Token Secret" className="w-full border rounded-lg px-3 py-2 text-sm" required />
            </div>
          </div>
        </>
      ) : (
        <div>
          <label className="block text-sm font-medium mb-1">{config.tokenLabel}</label>
          <input
            type="password"
            value={accessToken}
            onChange={(e) => setAccessToken(e.target.value)}
            placeholder={config.tokenPlaceholder}
            className="w-full border rounded-lg px-3 py-2 text-sm"
            required
          />
        </div>
      )}

      <button
        type="submit"
        disabled={saving}
        className="px-4 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
      >
        {saving ? 'Connecting...' : 'Connect'}
      </button>
    </form>
  )
}
