package com.railway.gateway.infrastructure.config;

import io.minio.MinioClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class MinioHealthIndicator implements HealthIndicator {

    private final MinioClient minioClient;

    @Override
    public Health health() {
        try {
            minioClient.listBuckets();
            return Health.up()
                    .withDetail("minio", "Available")
                    .build();
        } catch (Exception e) {
            log.error("MinIO health check failed", e);
            return Health.down()
                    .withDetail("minio", "Unavailable")
                    .withDetail("error", e.getMessage())
                    .build();
        }
    }
}