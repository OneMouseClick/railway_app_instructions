package com.railway.gateway.infrastructure.service;

import com.railway.gateway.domain.exception.infrastructure.BucketNotFoundException;
import com.railway.gateway.domain.exception.infrastructure.FileDownloadException;
import com.railway.gateway.domain.exception.infrastructure.FileUploadException;
import com.railway.gateway.domain.exception.infrastructure.ObjectNotFoundException;
import com.railway.gateway.domain.service.MinioService;
import com.railway.gateway.domain.valueobject.BucketType;
import io.minio.BucketExistsArgs;
import io.minio.CopyObjectArgs;
import io.minio.CopySource;
import io.minio.GetObjectArgs;
import io.minio.GetObjectResponse;
import io.minio.MakeBucketArgs;
import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import io.minio.RemoveObjectArgs;
import io.minio.StatObjectArgs;
import io.minio.StatObjectResponse;
import io.minio.errors.ErrorResponseException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.io.InputStream;
import java.time.LocalDate;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class MinioServiceImpl implements MinioService {

    private final MinioClient minioClient;

    @Override
    public void upload(BucketType bucketType, String objectKey, InputStream inputStream, long size, String contentType) {
        try {
            ensureBucketExists(bucketType);

            minioClient.putObject(
                    PutObjectArgs.builder()
                            .bucket(bucketType.getBucketName())
                            .object(objectKey)
                            .stream(inputStream, size, -1)
                            .contentType(contentType)
                            .build()
            );

            log.debug("File uploaded successfully. Bucket: {}, ObjectKey: {}, Size: {} bytes",
                    bucketType.getBucketName(), objectKey, size);
        } catch (Exception e) {
            log.error("Failed to upload file. Bucket: {}, ObjectKey: {}", bucketType.getBucketName(), objectKey, e);
            throw new FileUploadException(bucketType, objectKey, e);
        }
    }

    @Override
    public InputStream download(BucketType bucketType, String objectKey) {
        try {
            GetObjectResponse response = minioClient.getObject(
                    GetObjectArgs.builder()
                            .bucket(bucketType.getBucketName())
                            .object(objectKey)
                            .build()
            );

            log.debug("File downloaded successfully. Bucket: {}, ObjectKey: {}", bucketType.getBucketName(), objectKey);
            return response;
        } catch (ErrorResponseException e) {
            if ("NoSuchKey".equals(e.errorResponse().code())) {
                throw new ObjectNotFoundException(bucketType, objectKey, e);
            }
            throw new FileDownloadException(bucketType, objectKey, e);
        } catch (Exception e) {
            log.error("Failed to download file. Bucket: {}, ObjectKey: {}", bucketType.getBucketName(), objectKey, e);
            throw new FileDownloadException(bucketType, objectKey, e);
        }
    }

    @Override
    public void delete(BucketType bucketType, String objectKey) {
        try {
            minioClient.removeObject(
                    RemoveObjectArgs.builder()
                            .bucket(bucketType.getBucketName())
                            .object(objectKey)
                            .build()
            );

            log.debug("File deleted successfully. Bucket: {}, ObjectKey: {}", bucketType.getBucketName(), objectKey);
        } catch (Exception e) {
            log.error("Failed to delete file. Bucket: {}, ObjectKey: {}", bucketType.getBucketName(), objectKey, e);
            throw new ObjectNotFoundException(bucketType, objectKey, e);
        }
    }

    @Override
    public boolean exists(BucketType bucketType, String objectKey) {
        try {
            minioClient.statObject(
                    StatObjectArgs.builder()
                            .bucket(bucketType.getBucketName())
                            .object(objectKey)
                            .build()
            );
            return true;
        } catch (ErrorResponseException e) {
            if ("NoSuchKey".equals(e.errorResponse().code())) {
                return false;
            }
            log.error("Error checking object existence. Bucket: {}, ObjectKey: {}", bucketType.getBucketName(), objectKey, e);
            return false;
        } catch (Exception e) {
            log.error("Error checking object existence. Bucket: {}, ObjectKey: {}", bucketType.getBucketName(), objectKey, e);
            return false;
        }
    }

    @Override
    public void copy(BucketType sourceBucket, String sourceObjectKey, BucketType destinationBucket, String destinationObjectKey) {
        try {
            ensureBucketExists(destinationBucket);

            minioClient.copyObject(
                    CopyObjectArgs.builder()
                            .bucket(destinationBucket.getBucketName())
                            .object(destinationObjectKey)
                            .source(CopySource.builder()
                                    .bucket(sourceBucket.getBucketName())
                                    .object(sourceObjectKey)
                                    .build())
                            .build()
            );

            log.debug("File copied successfully. From: {}/{}, To: {}/{}",
                    sourceBucket.getBucketName(), sourceObjectKey,
                    destinationBucket.getBucketName(), destinationObjectKey);
        } catch (Exception e) {
            log.error("Failed to copy file. From: {}/{}, To: {}/{}",
                    sourceBucket.getBucketName(), sourceObjectKey,
                    destinationBucket.getBucketName(), destinationObjectKey, e);
            throw new FileUploadException(destinationBucket, destinationObjectKey, e);
        }
    }

    @Override
    public Map<String, String> getMetadata(BucketType bucketType, String objectKey) {
        try {
            StatObjectResponse stat = minioClient.statObject(
                    StatObjectArgs.builder()
                            .bucket(bucketType.getBucketName())
                            .object(objectKey)
                            .build()
            );

            Map<String, String> metadata = new HashMap<>();
            metadata.put("size", String.valueOf(stat.size()));
            metadata.put("contentType", stat.contentType());
            metadata.put("lastModified", stat.lastModified().toString());
            metadata.put("etag", stat.etag());

            if (stat.userMetadata() != null) {
                metadata.putAll(stat.userMetadata());
            }

            return metadata;
        } catch (ErrorResponseException e) {
            if ("NoSuchKey".equals(e.errorResponse().code())) {
                throw new ObjectNotFoundException(bucketType, objectKey, e);
            }
            throw new FileDownloadException(bucketType, objectKey, e);
        } catch (Exception e) {
            log.error("Failed to get metadata. Bucket: {}, ObjectKey: {}", bucketType.getBucketName(), objectKey, e);
            throw new FileDownloadException(bucketType, objectKey, e);
        }
    }

    @Override
    public String generateObjectKey(UUID taskId, String originalFileName) {
        LocalDate now = LocalDate.now();
        String extension = getFileExtension(originalFileName);
        String uniqueName = UUID.randomUUID().toString();

        return String.format("%s/%s/%s/source/%s%s",
                now.getYear(),
                String.format("%02d", now.getMonthValue()),
                taskId,
                uniqueName,
                extension);
    }

    @Override
    public String generateObjectKey(BucketType bucketType, UUID taskId, String suffix) {
        LocalDate now = LocalDate.now();
        String uniqueName = UUID.randomUUID().toString();

        return switch (bucketType) {
            case SOURCE_DOCUMENTS -> String.format("%s/%s/%s/source/%s%s",
                    now.getYear(),
                    String.format("%02d", now.getMonthValue()),
                    taskId,
                    uniqueName,
                    suffix);
            case PARSED_JSON -> String.format("%s/%s/%s/parsed/%s%s",
                    now.getYear(),
                    String.format("%02d", now.getMonthValue()),
                    taskId,
                    uniqueName,
                    suffix);
            case GENERATED_JSON -> String.format("%s/%s/%s/generated/%s%s",
                    now.getYear(),
                    String.format("%02d", now.getMonthValue()),
                    taskId,
                    uniqueName,
                    suffix);
            case RESULT_DOCUMENTS -> String.format("%s/%s/%s/result/%s%s",
                    now.getYear(),
                    String.format("%02d", now.getMonthValue()),
                    taskId,
                    uniqueName,
                    suffix);
        };
    }

    @Override
    public void ensureBucketExists(BucketType bucketType) {
        try {
            boolean exists = minioClient.bucketExists(
                    BucketExistsArgs.builder()
                            .bucket(bucketType.getBucketName())
                            .build()
            );

            if (!exists) {
                minioClient.makeBucket(
                        MakeBucketArgs.builder()
                                .bucket(bucketType.getBucketName())
                                .build()
                );
                log.info("Bucket created: {}", bucketType.getBucketName());
            }
        } catch (Exception e) {
            log.error("Failed to ensure bucket exists: {}", bucketType.getBucketName(), e);
            throw new BucketNotFoundException(bucketType, e);
        }
    }

    private String getFileExtension(String fileName) {
        if (fileName == null || fileName.isEmpty()) {
            return "";
        }
        int lastDotIndex = fileName.lastIndexOf('.');
        if (lastDotIndex == -1 || lastDotIndex == fileName.length() - 1) {
            return "";
        }
        return fileName.substring(lastDotIndex).toLowerCase();
    }
}