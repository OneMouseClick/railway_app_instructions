package com.railway.gateway.infrastructure.properties;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

@Data
@Validated
@ConfigurationProperties(prefix = "minio")
public class MinioProperties {

    @NotBlank
    private String endpoint;

    @NotBlank
    private String accessKey;

    @NotBlank
    private String secretKey;

    @NotNull
    private Boolean secure = false;

    private int connectionTimeout = 60000;
    private int readTimeout = 60000;
    private int writeTimeout = 60000;
    private int maxIdleConnections = 10;
    private int keepAliveDuration = 30000;
}