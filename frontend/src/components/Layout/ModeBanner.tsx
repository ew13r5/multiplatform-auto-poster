interface ModeBannerProps {
  mode: string
}

export default function ModeBanner({ mode }: ModeBannerProps) {
  if (mode !== 'development') return null
  return (
    <div className="bg-yellow-50 border-b border-yellow-200 px-4 py-2 text-sm text-yellow-800">
      Development Mode — posts visible only to testers
    </div>
  )
}
