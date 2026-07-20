package com.railway.gateway.infrastructure.config;

import com.railway.gateway.domain.valueobject.BucketType;
import com.railway.gateway.infrastructure.properties.MinioProperties;
import io.minio.BucketExistsArgs;
import io.minio.MakeBucketArgs;
import io.minio.MinioClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import okhttp3.OkHttpClient;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.concurrent.TimeUnit;

@Slf4j
@Configuration
@RequiredArgsConstructor
public class MinioConfig {

    private final MinioProperties minioProperties;

    @Bean
    public MinioClient minioClient() {
        OkHttpClient httpClient = new OkHttpClient.Builder()
                .connectTimeout(minioProperties.getConnectionTimeout(), TimeUnit.MILLISECONDS)
                .readTimeout(minioProperties.getReadTimeout(), TimeUnit.MILLISECONDS)
                .writeTimeout(minioProperties.getWriteTimeout(), TimeUnit.MILLISECONDS)
                .connectionPool(new okhttp3.ConnectionPool(
                        minioProperties.getMaxIdleConnections(),
                        minioProperties.getKeepAliveDuration(),
                        TimeUnit.MILLISECONDS))
                .build();

        MinioClient minioClient = MinioClient.builder()
                .endpoint(minioProperties.getEndpoint())
                .credentials(minioProperties.getAccessKey(), minioProperties.getSecretKey())
                .httpClient(httpClient)
                .build();

        initBuckets(minioClient);

        log.info("MinioClient configured with endpoint: {}, secure: {}",
                minioProperties.getEndpoint(), minioProperties.getSecure());
        return minioClient;
    }

    private void initBuckets(MinioClient minioClient) {
        for (BucketType bucketType : BucketType.values()) {
            try {
                boolean exists = minioClient.bucketExists(
                        BucketExistsArgs.builder().bucket(bucketType.getBucketName()).build()
                );
                if (!exists) {
                    minioClient.makeBucket(
                            MakeBucketArgs.builder().bucket(bucketType.getBucketName()).build()
                    );
                    log.info("Bucket created: {}", bucketType.getBucketName());
                } else {
                    log.debug("Bucket already exists: {}", bucketType.getBucketName());
                }
            } catch (Exception e) {
                log.error("Failed to initialize bucket: {}", bucketType.getBucketName(), e);
            }
        }
    }
}