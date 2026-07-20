package com.railway.gateway.domain.exception.infrastructure;

import com.railway.gateway.domain.valueobject.BucketType;

public class FileDownloadException extends RuntimeException {

    public FileDownloadException(BucketType bucketType, String objectKey) {
        super("Failed to download file from bucket '%s' with key: %s".formatted(bucketType.getBucketName(), objectKey));
    }

    public FileDownloadException(BucketType bucketType, String objectKey, Throwable cause) {
        super("Failed to download file from bucket '%s' with key: %s".formatted(bucketType.getBucketName(), objectKey), cause);
    }
}