package com.railway.gateway.domain.exception.infrastructure;

import com.railway.gateway.domain.valueobject.BucketType;

public class FileUploadException extends RuntimeException {

    public FileUploadException(BucketType bucketType, String objectKey) {
        super("Failed to upload file to bucket '%s' with key: %s".formatted(bucketType.getBucketName(), objectKey));
    }

    public FileUploadException(BucketType bucketType, String objectKey, Throwable cause) {
        super("Failed to upload file to bucket '%s' with key: %s".formatted(bucketType.getBucketName(), objectKey), cause);
    }
}