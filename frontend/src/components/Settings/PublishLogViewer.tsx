import { useEffect, useState } from 'react'
import type { PublishLogEntry } from '../../types/log'
import type { Page } from '../../types/page'
import { getLog } from '../../api/health'
import LoadingSpinner from '../shared/LoadingSpinner'

interface PublishLogViewerProps {
  pages: Page[]
}

export default function PublishLogViewer({ pages }: PublishLogViewerProps) {
  const [entries, setEntries] = useState<PublishLogEntry[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [pageFilter, setPageFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [offset, setOffset] = useState(0)
  const limit = 20

  useEffect(() => {
    setLoading(true)
    const params: Record<string, string | number> = { limit, offset }
    if (pageFilter) params.page_id = pageFilter
    if (statusFilter) params.status = statusFilter

    getLog(params)
      .then((data) => {
        setEntries(data.entries)
        setTotal(data.total)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [pageFilter, statusFilter, offset])

  return (
    <div className="space-y-3">
      <div className="flex gap-3">
        <select
          value={pageFilter}
          onChange={(e) => { setPageFilter(e.target.value); setOffset(0) }}
          className="border rounded-lg px-3 py-1.5 text-sm"
        >
          <option value="">All Pages</option>
          {pages.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setOffset(0) }}
          className="border rounded-lg px-3 py-1.5 text-sm"
        >
          <option value="">All Status</option>
          <option value="success">Success</option>
          <option value="error">Error</option>
        </select>
      </div>

      {loading ? (
        <LoadingSpinner size="sm" />
      ) : entries.length === 0 ? (
        <p className="text-sm text-gray-500">No log entries.</p>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b">
                  <th className="py-2 pr-3 font-medium text-gray-700">Time</th>
                  <th className="py-2 pr-3 font-medium text-gray-700">Page</th>
                  <th className="py-2 pr-3 font-medium text-gray-700">Content</th>
                  <th className="py-2 pr-3 font-medium text-gray-700">Status</th>
                  <th className="py-2 pr-3 font-medium text-gray-700">Error</th>
                  <th className="py-2 font-medium text-gray-700">Retries</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((entry, i) => (
                  <tr key={i} className="border-b last:border-b-0">
                    <td className="py-2 pr-3 text-gray-500 whitespace-nowrap">
                      {new Date(entry.attempted_at).toLocaleString('en-US')}
                    </td>
                    <td className="py-2 pr-3">{entry.page_name}</td>
                    <td className="py-2 pr-3 max-w-[150px] truncate">{entry.content_preview}</td>
                    <td className="py-2 pr-3">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${
                        entry.result === 'success'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-red-100 text-red-700'
                      }`}>
                        {entry.result}
                      </span>
                    </td>
                    <td className="py-2 pr-3 text-xs text-gray-500 max-w-[200px] truncate">
                      {entry.error_message || '—'}
                    </td>
                    <td className="py-2 text-center">{entry.retry_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {total > offset + limit && (
            <div className="text-center">
              <button
                onClick={() => setOffset((o) => o + limit)}
                className="text-sm text-blue-500 hover:text-blue-700"
              >
                Load More
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
