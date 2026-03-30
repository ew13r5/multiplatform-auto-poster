import { useCallback, useEffect, useState } from 'react'
import type { Page } from '../types/page'
import { getPages } from '../api/pages'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import ErrorState from '../components/shared/ErrorState'
import Card from '../components/shared/Card'
import ConnectPageForm from '../components/Settings/ConnectPageForm'
import ConnectedPages from '../components/Settings/ConnectedPages'
import AlertConfigPanel from '../components/Settings/AlertConfigPanel'
import PublishLogViewer from '../components/Settings/PublishLogViewer'

export default function Settings() {
  const [pages, setPages] = useState<Page[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshCounter, setRefreshCounter] = useState(0)

  const refresh = useCallback(() => setRefreshCounter((c) => c + 1), [])

  useEffect(() => {
    setLoading(true)
    getPages()
      .then(setPages)
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load'))
      .finally(() => setLoading(false))
  }, [refreshCounter])

  if (loading) return <div className="p-6 flex justify-center"><LoadingSpinner /></div>
  if (error) return <div className="p-6"><ErrorState message={error} onRetry={refresh} /></div>

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>

      <Card title="Connect Channel">
        <ConnectPageForm onConnected={refresh} />
      </Card>

      <Card title="Connected Pages">
        <ConnectedPages pages={pages} />
      </Card>

      <Card title="Alert Configuration">
        <AlertConfigPanel />
      </Card>

      <Card title="Publishing Log">
        <PublishLogViewer pages={pages} />
      </Card>
    </div>
  )
}
