"""RabbitMQ worker: TASK_CREATED → parse → PARSED / FAILED."""

from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path

from app.messaging import base_event, connect_with_retry, consume_queue, publish_event
from app.pipeline import parse_tech_passport
from app.storage import build_parsed_object_key, create_minio_client, download_bytes, upload_json

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("document-worker")

SOURCE_BUCKET = os.getenv("MINIO_SOURCE_BUCKET", "source-documents")
PARSED_BUCKET = os.getenv("MINIO_PARSED_BUCKET", "parsed-json")
TASK_EXCHANGE = os.getenv("RABBITMQ_TASK_EXCHANGE", "task.exchange")
STATUS_RK = os.getenv("RABBITMQ_STATUS_RK", "task.status")
PARSE_QUEUE = os.getenv("RABBITMQ_PARSE_QUEUE", "document.parse.queue")


def _publish_status(event: dict) -> None:
    connection = connect_with_retry()
    try:
        channel = connection.channel()
        publish_event(channel, TASK_EXCHANGE, STATUS_RK, event)
    finally:
        connection.close()


def handle_task_created(event: dict) -> None:
    event_type = event.get("eventType")
    if event_type not in ("TASK_CREATED", "DOCUMENT_UPLOADED"):
        log.warning("Skip unexpected eventType=%s", event_type)
        return

    task_id = str(event["taskId"])
    object_key = event.get("minioObjectKey")
    original_name = event.get("originalFileName") or "document.pdf"

    if not object_key:
        raise ValueError("minioObjectKey is required")

    _publish_status(base_event("PARSING_STARTED", task_id))

    minio = create_minio_client()
    file_bytes = download_bytes(minio, SOURCE_BUCKET, object_key)
    suffix = Path(original_name).suffix.lower() or Path(object_key).suffix.lower() or ".pdf"

    with tempfile.TemporaryDirectory(prefix="tp_worker_") as tmpdir:
        local_path = Path(tmpdir) / f"source{suffix}"
        local_path.write_bytes(file_bytes)
        parsed = parse_tech_passport(str(local_path), original_filename=original_name)

    payload = json.dumps(parsed, ensure_ascii=False, indent=2).encode("utf-8")
    parsed_key = build_parsed_object_key(task_id)
    upload_json(minio, PARSED_BUCKET, parsed_key, payload)

    _publish_status(
        base_event("PARSED", task_id, parsedContentObjectKey=parsed_key)
    )
    log.info("Parsed taskId=%s → %s", task_id, parsed_key)


def handle_with_failure(event: dict) -> None:
    task_id = str(event.get("taskId") or "")
    try:
        handle_task_created(event)
    except Exception as exc:  # noqa: BLE001
        log.exception("Document processing failed taskId=%s", task_id)
        if task_id:
            _publish_status(
                base_event("FAILED", task_id, errorMessage=str(exc)[:2000])
            )
        raise


def main() -> None:
    log.info("Document worker starting, queue=%s", PARSE_QUEUE)
    consume_queue(PARSE_QUEUE, handle_with_failure)


if __name__ == "__main__":
    main()
