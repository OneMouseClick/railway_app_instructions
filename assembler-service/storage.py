"""MinIO client for assembler-service."""

from __future__ import annotations

import io
import json
import os
from datetime import datetime, timezone
from uuid import uuid4

from minio import Minio


def create_minio_client() -> Minio:
    endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000").replace("http://", "").replace("https://", "")
    return Minio(
        endpoint,
        access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
    )


def download_json(client: Minio, bucket: str, object_key: str) -> dict:
    response = client.get_object(bucket, object_key)
    try:
        return json.loads(response.read().decode("utf-8"))
    finally:
        response.close()
        response.release_conn()


def upload_bytes(
    client: Minio,
    bucket: str,
    object_key: str,
    data: bytes,
    content_type: str,
) -> str:
    client.put_object(
        bucket,
        object_key,
        io.BytesIO(data),
        length=len(data),
        content_type=content_type,
    )
    return object_key


def build_result_object_key(task_id: str, ext: str = "pdf") -> str:
    now = datetime.now(timezone.utc)
    return f"{now:%Y}/{now:%m}/{task_id}/result/{uuid4()}.{ext.lstrip('.')}"
