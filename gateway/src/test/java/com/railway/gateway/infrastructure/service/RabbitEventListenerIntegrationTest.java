package com.railway.gateway.infrastructure.service;

import com.railway.gateway.domain.entity.Task;
import com.railway.gateway.domain.entity.User;
import com.railway.gateway.domain.enums.TaskStatus;
import com.railway.gateway.domain.enums.UserRole;
import com.railway.gateway.domain.event.CompletedEvent;
import com.railway.gateway.domain.event.FailedEvent;
import com.railway.gateway.domain.event.GeneratedEvent;
import com.railway.gateway.domain.event.ParsedEvent;
import com.railway.gateway.domain.event.ParsingStartedEvent;
import com.railway.gateway.domain.repository.TaskRepository;
import com.railway.gateway.domain.repository.UserRepository;
import com.railway.gateway.domain.service.EventPublisher;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.containers.RabbitMQContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;

import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.awaitility.Awaitility.await;

@SpringBootTest
@Testcontainers
class RabbitEventListenerIntegrationTest {

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
    private TaskRepository taskRepository;

    @Autowired
    private UserRepository userRepository;

    private UUID taskId;

    @BeforeEach
    void setUp() {
        User user = User.builder()
                .username("eventuser-" + UUID.randomUUID().toString().substring(0, 8))
                .email("eventuser-" + UUID.randomUUID().toString().substring(0, 8) + "@railway.com")
                .passwordHash("hash")
                .role(UserRole.USER)
                .enabled(true)
                .build();
        user = userRepository.save(user);

        Task task = Task.builder()
                .user(user)
                .originalFileName("test.pdf")
                .originalFileType("application/pdf")
                .minioObjectName("source/test.pdf")
                .status(TaskStatus.CREATED)
                .build();

        task = taskRepository.save(task);
        taskId = task.getId();
    }

    @AfterEach
    void tearDown() {
        taskRepository.deleteAll();
        userRepository.deleteAll();
    }

    @Test
    void shouldHandleParsingStartedEvent() {
        ParsingStartedEvent event = new ParsingStartedEvent(taskId);
        eventPublisher.publish(event);

        await().untilAsserted(() -> {
            Optional<Task> updated = taskRepository.findById(taskId);
            assertThat(updated).isPresent();
            assertThat(updated.get().getStatus()).isEqualTo(TaskStatus.PARSING);
        });
    }

    @Test
    void shouldHandleParsedEvent() {
        ParsedEvent event = new ParsedEvent(taskId, "parsed/2026/07/test.json");
        eventPublisher.publish(event);

        await().untilAsserted(() -> {
            Optional<Task> updated = taskRepository.findById(taskId);
            assertThat(updated).isPresent();
            assertThat(updated.get().getStatus()).isEqualTo(TaskStatus.PARSED);
            assertThat(updated.get().getParsedContentObjectKey()).isEqualTo("parsed/2026/07/test.json");
        });
    }

    @Test
    void shouldHandleGeneratedEvent() {
        GeneratedEvent event = new GeneratedEvent(taskId, "generated/2026/07/test.json");
        eventPublisher.publish(event);

        await().untilAsserted(() -> {
            Optional<Task> updated = taskRepository.findById(taskId);
            assertThat(updated).isPresent();
            assertThat(updated.get().getStatus()).isEqualTo(TaskStatus.GENERATED);
            assertThat(updated.get().getGeneratedInstructionObjectKey()).isEqualTo("generated/2026/07/test.json");
        });
    }

    @Test
    void shouldHandleCompletedEvent() {
        CompletedEvent event = new CompletedEvent(taskId, "result/2026/07/test.pdf");
        eventPublisher.publish(event);

        await().untilAsserted(() -> {
            Optional<Task> updated = taskRepository.findById(taskId);
            assertThat(updated).isPresent();
            assertThat(updated.get().getStatus()).isEqualTo(TaskStatus.COMPLETED);
            assertThat(updated.get().getResultMinioObjectName()).isEqualTo("result/2026/07/test.pdf");
        });
    }

    @Test
    void shouldHandleFailedEvent() {
        FailedEvent event = new FailedEvent(taskId, "Document parsing failed: invalid format");
        eventPublisher.publish(event);

        await().untilAsserted(() -> {
            Optional<Task> updated = taskRepository.findById(taskId);
            assertThat(updated).isPresent();
            assertThat(updated.get().getStatus()).isEqualTo(TaskStatus.FAILED);
            assertThat(updated.get().getErrorMessage()).isEqualTo("Document parsing failed: invalid format");
        });
    }

    @Test
    void shouldNotFailWhenTaskNotFound() {
        UUID nonExistentTaskId = UUID.randomUUID();
        ParsingStartedEvent event = new ParsingStartedEvent(nonExistentTaskId);

        eventPublisher.publish(event);

        await().during(2, java.util.concurrent.TimeUnit.SECONDS).until(() -> true);
    }
}