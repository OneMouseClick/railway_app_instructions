package com.railway.gateway.domain.service;

import com.railway.gateway.domain.valueobject.BucketType;

import java.io.InputStream;
import java.util.Map;
import java.util.UUID;

public interface MinioService {

    void upload(BucketType bucketType, String objectKey, InputStream inputStream, long size, String contentType);

    InputStream download(BucketType bucketType, String objectKey);

    void delete(BucketType bucketType, String objectKey);

    boolean exists(BucketType bucketType, String objectKey);

    void copy(BucketType sourceBucket, String sourceObjectKey, BucketType destinationBucket, String destinationObjectKey);

    Map<String, String> getMetadata(BucketType bucketType, String objectKey);

    String generateObjectKey(UUID taskId, String originalFileName);

    String generateObjectKey(BucketType bucketType, UUID taskId, String suffix);

    void ensureBucketExists(BucketType bucketType);
}