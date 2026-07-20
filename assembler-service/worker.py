"""RabbitMQ worker: GENERATED → assemble DOCX/PDF → COMPLETED / FAILED."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from docx_generator_v2 import generate_docx_bytes
from messaging import base_event, connect_with_retry, consume_queue, publish_event
from storage import (
    build_result_object_key,
    create_minio_client,
    download_json,
    upload_bytes,
)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("assembler-worker")

GENERATED_BUCKET = os.getenv("MINIO_GENERATED_BUCKET", "generated-json")
RESULT_BUCKET = os.getenv("MINIO_RESULT_BUCKET", "result-documents")
TASK_EXCHANGE = os.getenv("RABBITMQ_TASK_EXCHANGE", "task.exchange")
STATUS_RK = os.getenv("RABBITMQ_STATUS_RK", "task.status")
ASSEMBLE_QUEUE = os.getenv("RABBITMQ_ASSEMBLE_QUEUE", "assemble.document.queue")
LIBREOFFICE = os.getenv("LIBREOFFICE_PATH", "soffice")


def _publish_status(event: dict) -> None:
    connection = connect_with_retry()
    try:
        channel = connection.channel()
        publish_event(channel, TASK_EXCHANGE, STATUS_RK, event)
    finally:
        connection.close()


def _convert_docx_to_pdf(docx_path: Path, out_dir: Path) -> Path | None:
    soffice = shutil.which(LIBREOFFICE) or shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        log.warning("LibreOffice not found — uploading DOCX instead of PDF")
        return None

    cmd = [
        soffice,
        "--headless",
        "--nologo",
        "--nolockcheck",
        "--convert-to",
        "pdf",
        "--outdir",
        str(out_dir),
        str(docx_path),
    ]
    log.info("Converting DOCX→PDF: %s", " ".join(cmd))
    subprocess.run(cmd, check=True, capture_output=True, timeout=120)
    pdf_path = out_dir / f"{docx_path.stem}.pdf"
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not produced: {pdf_path}")
    return pdf_path


def handle_generated(event: dict) -> None:
    if event.get("eventType") != "GENERATED":
        log.warning("Skip unexpected eventType=%s", event.get("eventType"))
        return

    task_id = str(event["taskId"])
    generated_key = event.get("generatedInstructionObjectKey")
    if not generated_key:
        raise ValueError("generatedInstructionObjectKey is required")

    _publish_status(base_event("ASSEMBLING_STARTED", task_id))

    minio = create_minio_client()
    payload = download_json(minio, GENERATED_BUCKET, generated_key)
    docx_bytes = generate_docx_bytes(payload)

    with tempfile.TemporaryDirectory(prefix="assemble_") as tmpdir:
        tmp = Path(tmpdir)
        docx_path = tmp / "instruction.docx"
        docx_path.write_bytes(docx_bytes)

        pdf_path = _convert_docx_to_pdf(docx_path, tmp)
        if pdf_path is not None:
            result_bytes = pdf_path.read_bytes()
            result_key = build_result_object_key(task_id, "pdf")
            content_type = "application/pdf"
        else:
            result_bytes = docx_bytes
            result_key = build_result_object_key(task_id, "docx")
            content_type = (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        upload_bytes(minio, RESULT_BUCKET, result_key, result_bytes, content_type)

    _publish_status(
        base_event("COMPLETED", task_id, resultMinioObjectName=result_key)
    )
    log.info("Assembled taskId=%s → %s", task_id, result_key)


def handle_with_failure(event: dict) -> None:
    task_id = str(event.get("taskId") or "")
    try:
        handle_generated(event)
    except Exception as exc:  # noqa: BLE001
        log.exception("Assembler processing failed taskId=%s", task_id)
        if task_id:
            _publish_status(base_event("FAILED", task_id, errorMessage=str(exc)[:2000]))
        raise


def main() -> None:
    log.info("Assembler worker starting, queue=%s", ASSEMBLE_QUEUE)
    consume_queue(ASSEMBLE_QUEUE, handle_with_failure)


if __name__ == "__main__":
    main()
