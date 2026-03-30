import { useRef, useState } from 'react'
import { bulkImport } from '../../api/posts'
import { useToast } from '../shared/Toast'
import Modal from '../shared/Modal'

interface BulkImportModalProps {
  isOpen: boolean
  onClose: () => void
  onImported: () => void
}

export default function BulkImportModal({ isOpen, onClose, onImported }: BulkImportModalProps) {
  const toast = useToast()
  const fileRef = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)

  async function handleImport() {
    if (!file) return
    setUploading(true)
    try {
      await bulkImport(file)
      toast.success('Import started')
      setFile(null)
      if (fileRef.current) fileRef.current.value = ''
      onImported()
    } catch {
      toast.error('Import failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Bulk Import"
      footer={
        <button
          onClick={handleImport}
          disabled={!file || uploading}
          className="px-4 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
        >
          {uploading ? 'Importing...' : 'Import'}
        </button>
      }
    >
      <div className="space-y-4">
        <p className="text-sm text-gray-600">Upload a CSV or JSON file with posts to import.</p>
        <input
          ref={fileRef}
          type="file"
          accept=".csv,.json"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="text-sm"
        />
        {file && (
          <p className="text-sm text-gray-500">Selected: {file.name}</p>
        )}
      </div>
    </Modal>
  )
}
