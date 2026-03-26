import { useEffect, useRef, useState, useCallback } from 'react'

interface WSEvent {
  event: string
  [key: string]: unknown
}

export function useWebSocket() {
  const [lastEvent, setLastEvent] = useState<WSEvent | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const retryDelay = useRef(1000)

  const connect = useCallback(() => {
    const apiKey = import.meta.env.VITE_API_KEY || 'dev-api-key'
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws?token=${apiKey}`)

    ws.onopen = () => {
      setIsConnected(true)
      retryDelay.current = 1000
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setLastEvent(data)
      } catch {}
    }

    ws.onclose = () => {
      setIsConnected(false)
      // Auto-reconnect with exponential backoff
      setTimeout(() => {
        retryDelay.current = Math.min(retryDelay.current * 2, 30000)
        connect()
      }, retryDelay.current)
    }

    ws.onerror = () => ws.close()
    wsRef.current = ws
  }, [])

  useEffect(() => {
    connect()
    return () => wsRef.current?.close()
  }, [connect])

  return { lastEvent, isConnected }
}
