interface HeaderProps {
  title: string
}

export default function Header({ title }: HeaderProps) {
  return (
    <header className="border-b border-gray-200 px-6 py-4">
      <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
    </header>
  )
}
