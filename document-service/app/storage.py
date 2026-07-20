"""MinIO client for document-service."""

from __future__ import annotations

import io
import os
from datetime import datetime, timezone
from uuid import uuid4

from minio import Minio


def create_minio_client() -> Minio:
    endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000").replace("http://", "").replace("https://", "")
    access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
    return Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)


def download_bytes(client: Minio, bucket: str, object_key: str) -> bytes:
    response = client.get_object(bucket, object_key)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()


def upload_json(client: Minio, bucket: str, object_key: str, data: bytes) -> str:
    client.put_object(
        bucket,
        object_key,
        io.BytesIO(data),
        length=len(data),
        content_type="application/json",
    )
    return object_key


def build_parsed_object_key(task_id: str) -> str:
    now = datetime.now(timezone.utc)
    return f"{now:%Y}/{now:%m}/{task_id}/parsed/{uuid4()}.json"
