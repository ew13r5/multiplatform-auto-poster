import { useState } from 'react'
import { ShieldAlert, ShieldCheck } from 'lucide-react'
import type { Page } from '../../types/page'
import { verifyToken } from '../../api/pages'
import { useToast } from '../shared/Toast'

interface ConnectedPagesProps {
  pages: Page[]
}

const tokenIcons = {
  configured: { icon: ShieldCheck, color: 'text-green-500', label: 'Valid' },
  missing: { icon: ShieldAlert, color: 'text-red-500', label: 'Missing' },
}

export default function ConnectedPages({ pages }: ConnectedPagesProps) {
  const toast = useToast()
  const [verifying, setVerifying] = useState<string | null>(null)

  async function handleVerify(pageId: string) {
    setVerifying(pageId)
    try {
      await verifyToken(pageId)
      toast.success('Token verified')
    } catch {
      toast.error('Token verification failed')
    } finally {
      setVerifying(null)
    }
  }

  if (pages.length === 0) {
    return <p className="text-sm text-gray-500">No pages connected yet.</p>
  }

  return (
    <div className="space-y-2">
      {pages.map((page) => {
        const tokenInfo = tokenIcons[page.token_status] || tokenIcons.missing
        const TokenIcon = tokenInfo.icon
        return (
          <div key={page.id} className="flex items-center justify-between py-2 border-b last:border-b-0">
            <div className="flex items-center gap-3">
              <TokenIcon size={16} className={tokenInfo.color} />
              <div>
                <span className={`text-xs px-1.5 py-0.5 rounded font-medium mr-2 ${
                  page.platform === 'telegram' ? 'bg-blue-100 text-blue-700'
                    : page.platform === 'twitter' ? 'bg-gray-900 text-white'
                    : 'bg-indigo-100 text-indigo-700'
                }`}>
                  {page.platform === 'twitter' ? 'X' : (page.platform || 'facebook')}
                </span>
                <span className="text-sm font-medium">{page.name}</span>
                <span className="text-xs text-gray-400 ml-2">{page.fb_page_id}</span>
                {page.category && (
                  <span className="text-xs text-gray-400 ml-2">· {page.category}</span>
                )}
              </div>
            </div>
            <button
              onClick={() => handleVerify(page.id)}
              disabled={verifying === page.id}
              className="text-xs px-3 py-1 border rounded-lg hover:bg-gray-50 disabled:opacity-50"
            >
              {verifying === page.id ? 'Verifying...' : 'Verify Token'}
            </button>
          </div>
        )
      })}
    </div>
  )
}
