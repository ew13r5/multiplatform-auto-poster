export function timeAgo(date: string | null | undefined): string {
  if (!date) return 'Never'

  const now = Date.now()
  const then = new Date(date).getTime()
  const diff = Math.floor((now - then) / 1000)

  if (diff < 60) return 'just now'

  if (diff < 3600) {
    const minutes = Math.floor(diff / 60)
    return minutes === 1 ? '1 minute ago' : `${minutes} minutes ago`
  }

  if (diff < 86400) {
    const hours = Math.floor(diff / 3600)
    return hours === 1 ? '1 hour ago' : `${hours} hours ago`
  }

  const days = Math.floor(diff / 86400)
  return days === 1 ? '1 day ago' : `${days} days ago`
}
