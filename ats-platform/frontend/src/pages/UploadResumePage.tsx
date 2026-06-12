import { useState, useRef, useCallback } from 'react'
import { Upload, FileText, CheckCircle2, AlertCircle, X, UploadCloud } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useUploadResume } from '@/hooks/queries'
import { cn } from '@/lib/utils'
import { Candidate } from '@/types'

interface UploadedFile {
  file: File
  id: string
  status: 'pending' | 'uploading' | 'success' | 'error'
  error?: string
  candidate?: Candidate
}

export default function UploadResumePage() {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const uploadMutation = useUploadResume()

  const addFiles = useCallback((incoming: FileList | File[]) => {
    const valid = Array.from(incoming).filter((f) => {
      const ext = f.name.split('.').pop()?.toLowerCase()
      return ext === 'pdf' || ext === 'docx'
    })
    setFiles((prev) => [
      ...prev,
      ...valid.map((file) => ({
        file,
        id: `${Date.now()}-${Math.random()}`,
        status: 'pending' as const,
      })),
    ])
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)
      addFiles(e.dataTransfer.files)
    },
    [addFiles],
  )

  const uploadFile = async (entry: UploadedFile) => {
    setFiles((prev) =>
      prev.map((f) => (f.id === entry.id ? { ...f, status: 'uploading' as const } : f)),
    )
    try {
      const candidate = await uploadMutation.mutateAsync(entry.file)
      setFiles((prev) =>
        prev.map((f) => (f.id === entry.id ? { ...f, status: 'success' as const, candidate } : f)),
      )
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'Upload failed.'
      setFiles((prev) =>
        prev.map((f) => (f.id === entry.id ? { ...f, status: 'error' as const, error: msg } : f)),
      )
    }
  }

  const uploadAll = () => files.filter((f) => f.status === 'pending').forEach(uploadFile)
  const removeFile = (id: string) => setFiles((prev) => prev.filter((f) => f.id !== id))

  const pendingCount = files.filter((f) => f.status === 'pending').length
  const successCount = files.filter((f) => f.status === 'success').length

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Drop Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
        onDragLeave={() => setIsDragging(false)}
        onClick={() => fileInputRef.current?.click()}
        className={cn(
          'relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-12 text-center cursor-pointer transition-all duration-200 select-none',
          isDragging
            ? 'border-primary bg-primary/5 scale-[1.01]'
            : 'border-border hover:border-primary/50 hover:bg-muted/30',
        )}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx"
          className="hidden"
          onChange={(e) => e.target.files && addFiles(e.target.files)}
        />
        <div className={cn(
          'flex h-16 w-16 items-center justify-center rounded-full transition-colors mb-4',
          isDragging ? 'bg-primary/15' : 'bg-muted',
        )}>
          <UploadCloud className={cn('h-7 w-7 transition-colors', isDragging ? 'text-primary' : 'text-muted-foreground')} />
        </div>
        <h3 className="text-base font-semibold text-foreground">
          {isDragging ? 'Drop files here' : 'Drag & drop resumes here'}
        </h3>
        <p className="mt-1.5 text-sm text-muted-foreground">
          or click to browse files
        </p>
        <div className="mt-4 flex gap-2">
          {['PDF', 'DOCX', 'Max 10MB'].map((tag) => (
            <span key={tag} className="inline-flex items-center rounded-full bg-secondary px-3 py-1 text-xs font-medium text-secondary-foreground">
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* Actions */}
      {files.length > 0 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            {files.length} file{files.length !== 1 ? 's' : ''} selected
            {successCount > 0 && ` · ${successCount} uploaded`}
          </p>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => setFiles([])}>
              Clear all
            </Button>
            <Button size="sm" onClick={uploadAll} disabled={pendingCount === 0}>
              <Upload className="mr-2 h-3.5 w-3.5" />
              Upload {pendingCount > 0 ? `${pendingCount} ` : ''}file{pendingCount !== 1 ? 's' : ''}
            </Button>
          </div>
        </div>
      )}

      {/* File list */}
      {files.length > 0 && (
        <div className="rounded-xl border border-border bg-card overflow-hidden">
          <div className="px-5 py-3 border-b border-border bg-muted/30">
            <h3 className="text-sm font-medium text-foreground">Resume Queue</h3>
          </div>
          <ul className="divide-y divide-border">
            {files.map((entry) => (
              <li key={entry.id} className="flex items-center gap-4 px-5 py-4">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 shrink-0">
                  <FileText className="h-4 w-4 text-blue-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">{entry.file.name}</p>
                  <div className="mt-0.5 flex items-center gap-2 text-xs text-muted-foreground">
                    <span>{(entry.file.size / 1024).toFixed(1)} KB</span>
                    {entry.status === 'success' && entry.candidate && (
                      <><span>·</span><span className="text-emerald-600 font-medium">Parsed as {entry.candidate.name}</span></>
                    )}
                    {entry.status === 'error' && (
                      <><span>·</span><span className="text-red-500">{entry.error}</span></>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  {entry.status === 'pending' && (
                    <Button variant="outline" size="sm" onClick={() => uploadFile(entry)} className="h-8 text-xs">
                      Upload
                    </Button>
                  )}
                  {entry.status === 'uploading' && (
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                      <div className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                      Uploading…
                    </div>
                  )}
                  {entry.status === 'success' && <CheckCircle2 className="h-4 w-4 text-emerald-500" />}
                  {entry.status === 'error' && <AlertCircle className="h-4 w-4 text-red-500" />}
                  <button onClick={() => removeFile(entry.id)} className="ml-1 text-muted-foreground hover:text-foreground">
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* How it works */}
      <div className="rounded-xl border border-border bg-card p-5">
        <h3 className="text-sm font-semibold text-foreground mb-3">How it works</h3>
        <ol className="space-y-2">
          {[
            'Upload one or multiple PDF or DOCX resume files',
            'The backend parses each file and extracts candidate information',
            'Candidates are added to your database automatically',
            'Phase 2 will use NLP (SpaCy) for deep skill and experience extraction',
          ].map((step, i) => (
            <li key={i} className="flex items-start gap-3 text-sm text-muted-foreground">
              <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary text-xs font-semibold">
                {i + 1}
              </span>
              {step}
            </li>
          ))}
        </ol>
      </div>
    </div>
  )
}
