import React, { useRef, useState } from 'react'

interface Props {
  onUpload: (file: File) => Promise<void>
  loading: boolean
}

export default function UploadResume({ onUpload, loading }: Props) {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [fileName, setFileName] = useState<string>('')

  const onFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (file.type !== 'application/pdf') {
      alert('Please upload a PDF file')
      return
    }
    setFileName(file.name)
    await onUpload(file)
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <div className="card">
      <h3 className="section-title">Upload your resume (PDF)</h3>
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        onChange={onFileChange}
        disabled={loading}
      />
      <div className="helper">{fileName ? `Selected: ${fileName}` : 'PDF only. Size < 10MB recommended.'}</div>
    </div>
  )
}
