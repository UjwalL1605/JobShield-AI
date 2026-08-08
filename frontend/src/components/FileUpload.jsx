import { useState, useRef } from 'react'
import { Upload, Image, X, CheckCircle } from 'lucide-react'
import './FileUpload.css'

function FileUpload({ onFileSelect, disabled = false }) {
  const [dragOver, setDragOver] = useState(false)
  const [preview, setPreview] = useState(null)
  const [fileName, setFileName] = useState('')
  const fileInputRef = useRef(null)

  const handleFile = (file) => {
    if (!file) return

    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp']
    if (!validTypes.includes(file.type)) {
      alert('Please upload a PNG, JPG, or WebP image.')
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      alert('File too large. Maximum size: 10MB')
      return
    }

    setFileName(file.name)

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => setPreview(e.target.result)
    reader.readAsDataURL(file)

    onFileSelect(file)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    handleFile(file)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = () => setDragOver(false)

  const handleClick = () => {
    if (!disabled) fileInputRef.current?.click()
  }

  const clearFile = (e) => {
    e.stopPropagation()
    setPreview(null)
    setFileName('')
    onFileSelect(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <div
      className={`file-upload ${dragOver ? 'file-upload-dragover' : ''} ${preview ? 'file-upload-has-file' : ''} ${disabled ? 'file-upload-disabled' : ''}`}
      onClick={handleClick}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept="image/png,image/jpeg,image/jpg,image/webp"
        onChange={(e) => handleFile(e.target.files[0])}
        hidden
      />

      {preview ? (
        <div className="file-upload-preview">
          <img src={preview} alt="Screenshot preview" className="file-upload-img" />
          <div className="file-upload-info">
            <div className="file-upload-success">
              <CheckCircle size={16} />
              <span>{fileName}</span>
            </div>
            <button className="file-upload-remove" onClick={clearFile}>
              <X size={16} />
              Remove
            </button>
          </div>
        </div>
      ) : (
        <div className="file-upload-placeholder">
          <div className="file-upload-icon">
            <Upload size={28} />
          </div>
          <p className="file-upload-text">
            <strong>Drop your screenshot here</strong> or click to browse
          </p>
          <p className="file-upload-hint">
            PNG, JPG, or WebP • Max 10MB
          </p>
          <div className="file-upload-formats">
            <span className="format-tag">WhatsApp</span>
            <span className="format-tag">Telegram</span>
            <span className="format-tag">LinkedIn</span>
            <span className="format-tag">Gmail</span>
            <span className="format-tag">SMS</span>
            <span className="format-tag">Instagram</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default FileUpload
