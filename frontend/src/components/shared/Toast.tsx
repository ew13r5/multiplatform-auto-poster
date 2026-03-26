import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { X } from 'lucide-react'

type ToastType = 'success' | 'error' | 'info'

interface ToastItem {
  id: number
  type: ToastType
  message: string
  timerId: ReturnType<typeof setTimeout>
}

interface ToastContextValue {
  success: (message: string) => void
  error: (message: string) => void
  info: (message: string) => void
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined)

const borderColors: Record<ToastType, string> = {
  success: 'border-l-4 border-green-500',
  error: 'border-l-4 border-red-500',
  info: 'border-l-4 border-blue-500',
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([])
  const idRef = useRef(0)

  const removeToast = useCallback((id: number) => {
    setToasts((prev) => {
      const toast = prev.find((t) => t.id === id)
      if (toast) clearTimeout(toast.timerId)
      return prev.filter((t) => t.id !== id)
    })
  }, [])

  const addToast = useCallback((type: ToastType, message: string) => {
    const id = ++idRef.current
    const timerId = setTimeout(() => removeToast(id), 5000)
    setToasts((prev) => [...prev, { id, type, message, timerId }])
  }, [removeToast])

  useEffect(() => {
    return () => {
      toasts.forEach((t) => clearTimeout(t.timerId))
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const value: ToastContextValue = {
    success: (msg) => addToast('success', msg),
    error: (msg) => addToast('error', msg),
    info: (msg) => addToast('info', msg),
  }

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`bg-white shadow-md rounded-lg p-4 min-w-[300px] ${borderColors[toast.type]}`}
            role="alert"
          >
            <div className="flex items-start justify-between gap-2">
              <p className="text-sm">{toast.message}</p>
              <button
                onClick={() => removeToast(toast.id)}
                className="text-gray-400 hover:text-gray-600 shrink-0"
              >
                <X size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}
