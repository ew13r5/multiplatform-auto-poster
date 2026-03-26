import { useState, useEffect, useCallback } from 'react'
import { getHealth, getLog } from '../api/health'
import { getPages } from '../api/pages'
import type { Page } from '../types/page'
import type { PublishLogEntry } from '../types/log'

interface HealthData {
  status: string
  checks: Record<string, boolean>
  mode: string
}

export function useDashboardData() {
  const [health, setHealth] = useState<HealthData | null>(null)
  const [pages, setPages] = useState<Page[]>([])
  const [logEntries, setLogEntries] = useState<PublishLogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [counter, setCounter] = useState(0)

  const refetch = useCallback(() => {
    setCounter((c) => c + 1)
  }, [])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    Promise.all([getHealth(), getPages(), getLog({ limit: 100 })])
      .then(([healthData, pagesData, logData]) => {
        if (cancelled) return
        setHealth(healthData)
        setPages(pagesData)
        setLogEntries(logData.entries)
        setLoading(false)
      })
      .catch((err: Error) => {
        if (cancelled) return
        setError(err.message)
        setLoading(false)
      })

    return () => { cancelled = true }
  }, [counter])

  return { health, pages, logEntries, loading, error, refetch }
}
