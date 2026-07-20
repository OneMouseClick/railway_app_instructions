"""RabbitMQ worker: PARSED → generate → GENERATED / FAILED."""

from __future__ import annotations

import logging
import os

from adapter import to_assembler_document
from generator import generate_instruction
from messaging import base_event, connect_with_retry, consume_queue, publish_event
from storage import (
    build_generated_object_key,
    create_minio_client,
    download_json,
    upload_json,
)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("ai-worker")

PARSED_BUCKET = os.getenv("MINIO_PARSED_BUCKET", "parsed-json")
GENERATED_BUCKET = os.getenv("MINIO_GENERATED_BUCKET", "generated-json")
TASK_EXCHANGE = os.getenv("RABBITMQ_TASK_EXCHANGE", "task.exchange")
STATUS_RK = os.getenv("RABBITMQ_STATUS_RK", "task.status")
AI_QUEUE = os.getenv("RABBITMQ_AI_QUEUE", "ai.analyze.queue")
DEFAULT_REGION = os.getenv("DEFAULT_REGION", "chita")


def _publish_status(event: dict) -> None:
    connection = connect_with_retry()
    try:
        channel = connection.channel()
        publish_event(channel, TASK_EXCHANGE, STATUS_RK, event)
    finally:
        connection.close()


def handle_parsed(event: dict) -> None:
    if event.get("eventType") != "PARSED":
        log.warning("Skip unexpected eventType=%s", event.get("eventType"))
        return

    task_id = str(event["taskId"])
    parsed_key = event.get("parsedContentObjectKey")
    if not parsed_key:
        raise ValueError("parsedContentObjectKey is required")

    _publish_status(base_event("GENERATING_STARTED", task_id))

    minio = create_minio_client()
    passport_data = download_json(minio, PARSED_BUCKET, parsed_key)
    ai_result = generate_instruction(passport_data)
    assembler_doc = to_assembler_document(
        task_id=task_id,
        passport_data=passport_data,
        ai_result=ai_result,
        region=DEFAULT_REGION,
    )

    generated_key = build_generated_object_key(task_id)
    upload_json(minio, GENERATED_BUCKET, generated_key, assembler_doc)

    _publish_status(
        base_event("GENERATED", task_id, generatedInstructionObjectKey=generated_key)
    )
    log.info("Generated taskId=%s → %s (mode=%s)", task_id, generated_key, ai_result.get("mode"))


def handle_with_failure(event: dict) -> None:
    task_id = str(event.get("taskId") or "")
    try:
        handle_parsed(event)
    except Exception as exc:  # noqa: BLE001
        log.exception("AI processing failed taskId=%s", task_id)
        if task_id:
            _publish_status(base_event("FAILED", task_id, errorMessage=str(exc)[:2000]))
        raise


def main() -> None:
    log.info("AI worker starting, queue=%s", AI_QUEUE)
    consume_queue(AI_QUEUE, handle_with_failure)


if __name__ == "__main__":
    main()
