import { Document, HeadingLevel, Packer, Paragraph, TextRun } from 'docx'
import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'

function safeFileName(value, extension) {
  const normalized = String(value || 'Инструкция')
    .replace(/[<>:"/\\|?*\u0000-\u001F]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 120)

  return `${normalized || 'Инструкция'}.${extension}`
}

function triggerBlobDownload(blob, fileName) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

export async function exportInstructionDocx({ content, title, station }) {
  const lines = String(content || '').split('\n')

  const paragraphs = lines.map((line) => {
    const trimmed = line.trim()

    if (!trimmed) return new Paragraph({ text: '' })

    if (trimmed.startsWith('РАЗДЕЛ')) {
      return new Paragraph({
        text: trimmed,
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 260, after: 120 },
      })
    }

    if (trimmed === 'ИНСТРУКЦИЯ' || trimmed === 'ПРИЛОЖЕНИЯ') {
      return new Paragraph({
        alignment: 'center',
        children: [new TextRun({ text: trimmed, bold: true, size: 30 })],
        spacing: { before: 240, after: 140 },
      })
    }

    const isApprovalLine = trimmed === 'УТВЕРЖДАЮ'
    return new Paragraph({
      alignment: isApprovalLine ? 'right' : 'left',
      children: [new TextRun({ text: trimmed, bold: isApprovalLine, size: 24 })],
      spacing: { after: 120 },
    })
  })

  const document = new Document({
    sections: [
      {
        properties: {
          page: {
            margin: { top: 1134, right: 850, bottom: 1134, left: 1134 },
          },
        },
        children: paragraphs,
      },
    ],
  })

  const blob = await Packer.toBlob(document)
  triggerBlobDownload(blob, safeFileName(`${title} — ${station}`, 'docx'))
}

export async function exportInstructionPdf({ content, title, station }) {
  const exportElement = document.createElement('article')
  exportElement.className = 'pdf-export-document'
  exportElement.textContent = String(content || '')
  document.body.appendChild(exportElement)

  try {
    if (document.fonts?.ready) await document.fonts.ready

    const canvas = await html2canvas(exportElement, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#ffffff',
      logging: false,
      windowWidth: 1000,
    })

    const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    const margin = 12
    const printableWidth = pageWidth - margin * 2
    const printableHeight = pageHeight - margin * 2
    const imageWidth = printableWidth
    const imageHeight = (canvas.height * imageWidth) / canvas.width
    const imageData = canvas.toDataURL('image/jpeg', 0.96)

    let remainingHeight = imageHeight
    let imagePosition = margin

    pdf.addImage(imageData, 'JPEG', margin, imagePosition, imageWidth, imageHeight, undefined, 'FAST')
    remainingHeight -= printableHeight

    while (remainingHeight > 0) {
      pdf.addPage()
      imagePosition = margin - (imageHeight - remainingHeight)
      pdf.addImage(imageData, 'JPEG', margin, imagePosition, imageWidth, imageHeight, undefined, 'FAST')
      remainingHeight -= printableHeight
    }

    pdf.save(safeFileName(`${title} — ${station}`, 'pdf'))
  } finally {
    exportElement.remove()
  }
}
