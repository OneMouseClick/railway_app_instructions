package com.railway.gateway.domain.exception.infrastructure;

import com.railway.gateway.domain.valueobject.BucketType;

public class BucketNotFoundException extends RuntimeException {

    public BucketNotFoundException(BucketType bucketType) {
        super("Bucket not found: %s".formatted(bucketType.getBucketName()));
    }

    public BucketNotFoundException(BucketType bucketType, Throwable cause) {
        super("Bucket not found: %s".formatted(bucketType.getBucketName()), cause);
    }
}