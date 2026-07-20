package com.railway.gateway.infrastructure.service;

import com.railway.gateway.domain.event.DocumentUploadedEvent;
import com.railway.gateway.domain.service.EventPublisher;
import org.junit.jupiter.api.Test;
import org.springframework.amqp.core.Message;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.containers.RabbitMQContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;

import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@Testcontainers
class RabbitEventPublisherIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgresContainer = new PostgreSQLContainer<>("postgres:16-alpine");

    @Container
    static RabbitMQContainer rabbitMQContainer = new RabbitMQContainer("rabbitmq:3.13-management-alpine");

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

        registry.add("minio.endpoint", () -> "http://localhost:9000");
        registry.add("minio.access-key", () -> "minioadmin");
        registry.add("minio.secret-key", () -> "minioadmin");
        registry.add("minio.secure", () -> false);
    }

    @Autowired
    private EventPublisher eventPublisher;

    @Autowired
    private RabbitTemplate rabbitTemplate;

    @Test
    void shouldPublishAndReceiveDocumentUploadedEvent() {
        UUID taskId = UUID.randomUUID();

        DocumentUploadedEvent event = new DocumentUploadedEvent(
                taskId,
                UUID.randomUUID(),
                "test-document.pdf",
                "2026/07/" + taskId + "/source/test-uuid.pdf"
        );

        eventPublisher.publish(event);

        Message receivedMessage = rabbitTemplate.receive("document.parse.queue", 5000);

        assertThat(receivedMessage).isNotNull();
        assertThat(receivedMessage.getMessageProperties().getCorrelationId())
                .isEqualTo(taskId.toString());
        assertThat(receivedMessage.getMessageProperties().getMessageId())
                .isEqualTo(event.getEventId().toString());
    }

    @Test
    void shouldSerializeEventCorrectly() throws Exception {
        UUID taskId = UUID.randomUUID();
        UUID userId = UUID.randomUUID();

        DocumentUploadedEvent event = new DocumentUploadedEvent(
                taskId, userId, "test.pdf", "2026/07/" + taskId + "/source/test.pdf"
        );

        eventPublisher.publish(event);

        Message receivedMessage = rabbitTemplate.receive("document.parse.queue", 5000);

        assertThat(receivedMessage).isNotNull();

        String body = new String(receivedMessage.getBody());
        assertThat(body).contains("\"eventType\":\"DOCUMENT_UPLOADED\"");
        assertThat(body).contains("\"taskId\":\"" + taskId + "\"");
        assertThat(body).contains("\"userId\":\"" + userId + "\"");
    }

    @Test
    void shouldUseCorrectRoutingKey() {
        DocumentUploadedEvent event = new DocumentUploadedEvent(
                UUID.randomUUID(), UUID.randomUUID(), "test.pdf", "source/test.pdf"
        );

        eventPublisher.publish(event);

        Message receivedMessage = rabbitTemplate.receive("document.parse.queue", 5000);

        assertThat(receivedMessage).isNotNull();
        assertThat(receivedMessage.getMessageProperties().getReceivedRoutingKey())
                .isEqualTo("document.parse");
    }
}