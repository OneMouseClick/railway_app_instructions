package com.railway.gateway.domain.exception.infrastructure;

import com.railway.gateway.domain.valueobject.BucketType;

public class ObjectNotFoundException extends RuntimeException {

    public ObjectNotFoundException(BucketType bucketType, String objectKey) {
        super("Object not found in bucket '%s' with key: %s".formatted(bucketType.getBucketName(), objectKey));
    }

    public ObjectNotFoundException(BucketType bucketType, String objectKey, Throwable cause) {
        super("Object not found in bucket '%s' with key: %s".formatted(bucketType.getBucketName(), objectKey), cause);
    }
}