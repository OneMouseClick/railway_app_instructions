package com.railway.gateway.infrastructure.service;

import com.railway.gateway.domain.service.MinioService;
import com.railway.gateway.domain.valueobject.BucketType;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.MinIOContainer;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.containers.RabbitMQContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

@SpringBootTest
@Testcontainers
class MinioServiceImplIntegrationTest {

    private static final String TEST_CONTENT = "Test content for MinIO integration test";
    private static final String TEST_FILE_NAME = "test-document.pdf";

    @Container
    static PostgreSQLContainer<?> postgresContainer = new PostgreSQLContainer<>("postgres:16-alpine");

    @Container
    static RabbitMQContainer rabbitMQContainer = new RabbitMQContainer("rabbitmq:3.13-management-alpine");

    @Container
    static MinIOContainer minioContainer = new MinIOContainer(DockerImageName.parse("minio/minio:latest"));

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgresContainer::getJdbcUrl);
        registry.add("spring.datasource.username", postgresContainer::getUsername);
        registry.add("spring.datasource.password", postgresContainer::getPassword);

        registry.add("spring.rabbitmq.host", rabbitMQContainer::getHost);
        registry.add("spring.rabbitmq.port", rabbitMQContainer::getAmqpPort);
        registry.add("spring.rabbitmq.username", rabbitMQContainer::getAdminUsername);
        registry.add("spring.rabbitmq.password", rabbitMQContainer::getAdminPassword);

        registry.add("rabbitmq.host", rabbitMQContainer::getHost);
        registry.add("rabbitmq.port", rabbitMQContainer::getAmqpPort);
        registry.add("rabbitmq.username", rabbitMQContainer::getAdminUsername);
        registry.add("rabbitmq.password", rabbitMQContainer::getAdminPassword);

        registry.add("minio.endpoint", () -> "http://" + minioContainer.getHost() + ":" + minioContainer.getMappedPort(9000));
        registry.add("minio.access-key", minioContainer::getUserName);
        registry.add("minio.secret-key", minioContainer::getPassword);
        registry.add("minio.secure", () -> false);
    }

    @Autowired
    private MinioService minioService;

    private UUID taskId;
    private String objectKey;

    @BeforeEach
    void setUp() {
        taskId = UUID.randomUUID();
        objectKey = minioService.generateObjectKey(taskId, TEST_FILE_NAME);
        minioService.ensureBucketExists(BucketType.SOURCE_DOCUMENTS);
    }

    @AfterEach
    void tearDown() {
        try {
            if (minioService.exists(BucketType.SOURCE_DOCUMENTS, objectKey)) {
                minioService.delete(BucketType.SOURCE_DOCUMENTS, objectKey);
            }
        } catch (Exception e) {
            // Ignore cleanup errors
        }
    }

    @Test
    void shouldUploadFileSuccessfully() {
        byte[] content = TEST_CONTENT.getBytes(StandardCharsets.UTF_8);
        InputStream inputStream = new ByteArrayInputStream(content);

        assertDoesNotThrow(() ->
                minioService.upload(BucketType.SOURCE_DOCUMENTS, objectKey, inputStream, content.length, "application/pdf")
        );

        assertTrue(minioService.exists(BucketType.SOURCE_DOCUMENTS, objectKey));
    }

    @Test
    void shouldDownloadFileSuccessfully() throws IOException {
        byte[] content = TEST_CONTENT.getBytes(StandardCharsets.UTF_8);
        InputStream uploadStream = new ByteArrayInputStream(content);
        minioService.upload(BucketType.SOURCE_DOCUMENTS, objectKey, uploadStream, content.length, "application/pdf");

        try (InputStream downloadedStream = minioService.download(BucketType.SOURCE_DOCUMENTS, objectKey)) {
            assertThat(downloadedStream).isNotNull();
            byte[] downloadedBytes = downloadedStream.readAllBytes();
            assertThat(new String(downloadedBytes, StandardCharsets.UTF_8)).isEqualTo(TEST_CONTENT);
        }
    }

    @Test
    void shouldDeleteFileSuccessfully() {
        byte[] content = TEST_CONTENT.getBytes(StandardCharsets.UTF_8);
        InputStream uploadStream = new ByteArrayInputStream(content);
        minioService.upload(BucketType.SOURCE_DOCUMENTS, objectKey, uploadStream, content.length, "application/pdf");

        assertDoesNotThrow(() -> minioService.delete(BucketType.SOURCE_DOCUMENTS, objectKey));
        assertFalse(minioService.exists(BucketType.SOURCE_DOCUMENTS, objectKey));
    }

    @Test
    void shouldReturnFalseWhenFileDoesNotExist() {
        boolean exists = minioService.exists(BucketType.SOURCE_DOCUMENTS, "non-existent-file.pdf");
        assertFalse(exists);
    }

    @Test
    void shouldReturnTrueWhenFileExists() {
        byte[] content = TEST_CONTENT.getBytes(StandardCharsets.UTF_8);
        InputStream uploadStream = new ByteArrayInputStream(content);
        minioService.upload(BucketType.SOURCE_DOCUMENTS, objectKey, uploadStream, content.length, "application/pdf");

        assertTrue(minioService.exists(BucketType.SOURCE_DOCUMENTS, objectKey));
    }

    @Test
    void shouldCopyFileSuccessfully() {
        byte[] content = TEST_CONTENT.getBytes(StandardCharsets.UTF_8);
        InputStream uploadStream = new ByteArrayInputStream(content);
        minioService.upload(BucketType.SOURCE_DOCUMENTS, objectKey, uploadStream, content.length, "application/pdf");

        String destinationKey = minioService.generateObjectKey(BucketType.RESULT_DOCUMENTS, taskId, ".pdf");

        assertDoesNotThrow(() ->
                minioService.copy(BucketType.SOURCE_DOCUMENTS, objectKey, BucketType.RESULT_DOCUMENTS, destinationKey)
        );

        assertTrue(minioService.exists(BucketType.RESULT_DOCUMENTS, destinationKey));

        minioService.delete(BucketType.RESULT_DOCUMENTS, destinationKey);
    }

    @Test
    void shouldGetMetadataSuccessfully() {
        byte[] content = TEST_CONTENT.getBytes(StandardCharsets.UTF_8);
        InputStream uploadStream = new ByteArrayInputStream(content);
        minioService.upload(BucketType.SOURCE_DOCUMENTS, objectKey, uploadStream, content.length, "application/pdf");

        Map<String, String> metadata = minioService.getMetadata(BucketType.SOURCE_DOCUMENTS, objectKey);

        assertThat(metadata).isNotNull();
        assertThat(metadata).containsKey("size");
        assertThat(metadata).containsKey("contentType");
        assertThat(metadata.get("contentType")).isEqualTo("application/pdf");
        assertThat(Long.parseLong(metadata.get("size"))).isEqualTo(content.length);
    }
}