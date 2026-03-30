interface StatusTabsProps {
  selected: string
  onChange: (status: string) => void
}

const tabs = [
  { label: 'All', value: '' },
  { label: 'Draft', value: 'draft' },
  { label: 'Queued', value: 'queued' },
  { label: 'Published', value: 'published' },
  { label: 'Failed', value: 'failed' },
]

export default function StatusTabs({ selected, onChange }: StatusTabsProps) {
  return (
    <div className="flex gap-1">
      {tabs.map((tab) => (
        <button
          key={tab.value}
          onClick={() => onChange(tab.value)}
          className={`px-3 py-1.5 text-sm font-medium border-b-2 transition-colors ${
            selected === tab.value
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}
