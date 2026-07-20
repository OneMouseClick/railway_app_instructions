package com.railway.gateway.api.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.railway.gateway.api.dto.LoginResponse;
import com.railway.gateway.api.dto.RegisterRequest;
import com.railway.gateway.api.dto.TaskDetailsResponse;
import com.railway.gateway.api.dto.TaskPageResponse;
import com.railway.gateway.domain.entity.Task;
import com.railway.gateway.domain.enums.TaskStatus;
import com.railway.gateway.domain.repository.TaskRepository;
import com.railway.gateway.domain.repository.UserRepository;
import com.railway.gateway.domain.service.MinioService;
import com.railway.gateway.domain.valueobject.BucketType;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.testcontainers.containers.MinIOContainer;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.containers.RabbitMQContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
@Testcontainers
class TaskControllerIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgresContainer = new PostgreSQLContainer<>("postgres:16-alpine");

    @Container
    static RabbitMQContainer rabbitMQContainer = new RabbitMQContainer("rabbitmq:3.13-management-alpine");

    @Container
    static MinIOContainer minioContainer = new MinIOContainer("minio/minio:latest");

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
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private TaskRepository taskRepository;

    @Autowired
    private MinioService minioService;

    private String userAccessToken;
    private String otherUserAccessToken;

    @BeforeEach
    void setUp() throws Exception {
        taskRepository.deleteAll();
        userRepository.deleteAll();

        userAccessToken = registerAndGetAccessToken(
                "tasktestuser-" + UUID.randomUUID().toString().substring(0, 8),
                "tasktest-" + UUID.randomUUID().toString().substring(0, 8) + "@railway.com"
        );

        otherUserAccessToken = registerAndGetAccessToken(
                "otheruser-" + UUID.randomUUID().toString().substring(0, 8),
                "other-" + UUID.randomUUID().toString().substring(0, 8) + "@railway.com"
        );
    }

    @AfterEach
    void tearDown() {
        taskRepository.deleteAll();
        userRepository.deleteAll();
    }

    /* ==================== Создание задачи ==================== */

    @Test
    void shouldCreateTaskSuccessfully() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file", "test-document.pdf", MediaType.APPLICATION_PDF_VALUE, "Test PDF content".getBytes()
        );

        mockMvc.perform(multipart("/api/v1/tasks")
                        .file(file)
                        .header("Authorization", "Bearer " + userAccessToken))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").exists())
                .andExpect(jsonPath("$.status").value("CREATED"))
                .andExpect(jsonPath("$.originalFileName").value("test-document.pdf"))
                .andExpect(jsonPath("$.createdAt").exists());
    }

    @Test
    void shouldReturnBadRequestForEmptyFile() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file", "empty.pdf", MediaType.APPLICATION_PDF_VALUE, new byte[0]
        );

        mockMvc.perform(multipart("/api/v1/tasks")
                        .file(file)
                        .header("Authorization", "Bearer " + userAccessToken))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.title").value("File Validation Error"));
    }

    @Test
    void shouldReturnBadRequestForUnsupportedExtension() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file", "test.exe", MediaType.APPLICATION_OCTET_STREAM_VALUE, "test".getBytes()
        );

        mockMvc.perform(multipart("/api/v1/tasks")
                        .file(file)
                        .header("Authorization", "Bearer " + userAccessToken))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.title").value("File Validation Error"));
    }

    /* ==================== Получение задачи ==================== */

    @Test
    void shouldGetTaskDetails() throws Exception {
        String taskId = createTask(userAccessToken);

        MvcResult getResult = mockMvc.perform(get("/api/v1/tasks/{id}", taskId)
                        .header("Authorization", "Bearer " + userAccessToken))
                .andExpect(status().isOk())
                .andReturn();

        TaskDetailsResponse response = objectMapper.readValue(
                getResult.getResponse().getContentAsString(), TaskDetailsResponse.class);

        assertThat(response.id().toString()).isEqualTo(taskId);
        assertThat(response.status()).isEqualTo("CREATED");
        assertThat(response.originalFileName()).isEqualTo("test-document.pdf");
        assertThat(response.originalFileType()).isEqualTo("application/pdf");
        assertThat(response.resultAvailable()).isFalse();
    }

    @Test
    void shouldReturnNotFoundForNonExistentTask() throws Exception {
        UUID nonExistentId = UUID.randomUUID();

        mockMvc.perform(get("/api/v1/tasks/{id}", nonExistentId)
                        .header("Authorization", "Bearer " + userAccessToken))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.title").value("Task Not Found"));
    }

    @Test
    void shouldReturnNotFoundForOtherUserTask() throws Exception {
        String taskId = createTask(userAccessToken);

        mockMvc.perform(get("/api/v1/tasks/{id}", taskId)
                        .header("Authorization", "Bearer " + otherUserAccessToken))
                .andExpect(status().isNotFound());
    }

    /* ==================== Статус задачи ==================== */

    @Test
    void shouldGetTaskStatus() throws Exception {
        String taskId = createTask(userAccessToken);

        mockMvc.perform(get("/api/v1/tasks/{id}/status", taskId)
                        .header("Authorization", "Bearer " + userAccessToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(taskId))
                .andExpect(jsonPath("$.status").value("CREATED"));
    }

    /* ==================== Список задач ==================== */

    @Test
    void shouldGetEmptyTaskList() throws Exception {
        MvcResult result = mockMvc.perform(get("/api/v1/tasks")
                        .header("Authorization", "Bearer " + userAccessToken)
                        .param("page", "0")
                        .param("size", "10"))
                .andExpect(status().isOk())
                .andReturn();

        TaskPageResponse response = objectMapper.readValue(
                result.getResponse().getContentAsString(), TaskPageResponse.class);

        assertThat(response.tasks()).isEmpty();
        assertThat(response.totalElements()).isEqualTo(0);
    }

    @Test
    void shouldFilterTasksByStatus() throws Exception {
        createTask(userAccessToken);
        createTask(userAccessToken);

        MvcResult result = mockMvc.perform(get("/api/v1/tasks")
                        .header("Authorization", "Bearer " + userAccessToken)
                        .param("page", "0")
                        .param("size", "10")
                        .param("status", "CREATED"))
                .andExpect(status().isOk())
                .andReturn();

        TaskPageResponse response = objectMapper.readValue(
                result.getResponse().getContentAsString(), TaskPageResponse.class);

        assertThat(response.tasks()).hasSize(2);
        assertThat(response.tasks().get(0).status()).isEqualTo("CREATED");
    }

    @Test
    void shouldReturnBadRequestForInvalidStatus() throws Exception {
        mockMvc.perform(get("/api/v1/tasks")
                        .header("Authorization", "Bearer " + userAccessToken)
                        .param("status", "INVALID_STATUS"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.title").value("Invalid Status"));
    }

    @Test
    void shouldSupportPagination() throws Exception {
        for (int i = 0; i < 5; i++) {
            MockMultipartFile file = new MockMultipartFile(
                    "file", "test-" + i + ".pdf", MediaType.APPLICATION_PDF_VALUE, ("Test " + i).getBytes()
            );
            mockMvc.perform(multipart("/api/v1/tasks")
                            .file(file).header("Authorization", "Bearer " + userAccessToken))
                    .andExpect(status().isCreated());
        }

        MvcResult page1Result = mockMvc.perform(get("/api/v1/tasks")
                        .header("Authorization", "Bearer " + userAccessToken)
                        .param("page", "0")
                        .param("size", "2"))
                .andExpect(status().isOk())
                .andReturn();

        TaskPageResponse page1 = objectMapper.readValue(
                page1Result.getResponse().getContentAsString(), TaskPageResponse.class);

        assertThat(page1.tasks()).hasSize(2);
        assertThat(page1.totalElements()).isEqualTo(5);
        assertThat(page1.totalPages()).isEqualTo(3);

        MvcResult page2Result = mockMvc.perform(get("/api/v1/tasks")
                        .header("Authorization", "Bearer " + userAccessToken)
                        .param("page", "1")
                        .param("size", "2"))
                .andExpect(status().isOk())
                .andReturn();

        TaskPageResponse page2 = objectMapper.readValue(
                page2Result.getResponse().getContentAsString(), TaskPageResponse.class);

        assertThat(page2.tasks()).hasSize(2);
        assertThat(page2.currentPage()).isEqualTo(1);
    }

    /* ==================== Удаление задачи ==================== */

    @Test
    void shouldDeleteTaskSuccessfully() throws Exception {
        String taskId = createTask(userAccessToken);

        mockMvc.perform(delete("/api/v1/tasks/{id}", taskId)
                        .header("Authorization", "Bearer " + userAccessToken))
                .andExpect(status().isNoContent());

        mockMvc.perform(get("/api/v1/tasks/{id}", taskId)
                        .header("Authorization", "Bearer " + userAccessToken))
                .andExpect(status().isNotFound());
    }

    /* ==================== Скачивание результата ==================== */

    @Test
    void shouldDownloadCompletedTaskPdf() throws Exception {
        String taskId = createTask(userAccessToken);

        String resultObjectKey = minioService.generateObjectKey(BucketType.RESULT_DOCUMENTS, UUID.fromString(taskId), ".pdf");
        byte[] pdfContent = "%PDF-1.4 mock pdf content".getBytes();
        try (InputStream pdfStream = new ByteArrayInputStream(pdfContent)) {
            minioService.upload(BucketType.RESULT_DOCUMENTS, resultObjectKey, pdfStream, pdfContent.length, "application/pdf");
        }

        Task task = taskRepository.findById(UUID.fromString(taskId)).orElseThrow();
        task.setStatus(TaskStatus.COMPLETED);
        task.setResultMinioObjectName(resultObjectKey);
        taskRepository.save(task);

        mockMvc.perform(get("/api/v1/tasks/{id}/download", taskId)
                        .header("Authorization", "Bearer " + userAccessToken))
                .andExpect(status().isOk())
                .andExpect(header().string("Content-Type", "application/pdf"))
                .andExpect(header().string("Content-Disposition", "attachment; filename=\"station-instruction.pdf\""));
    }

    @Test
    void shouldReturnNotFoundWhenDownloadingOtherUserTask() throws Exception {
        String taskId = createTask(userAccessToken);

        String resultObjectKey = minioService.generateObjectKey(BucketType.RESULT_DOCUMENTS, UUID.fromString(taskId), ".pdf");
        byte[] pdfContent = "%PDF-1.4 mock pdf content".getBytes();
        try (InputStream pdfStream = new ByteArrayInputStream(pdfContent)) {
            minioService.upload(BucketType.RESULT_DOCUMENTS, resultObjectKey, pdfStream, pdfContent.length, "application/pdf");
        }

        Task task = taskRepository.findById(UUID.fromString(taskId)).orElseThrow();
        task.setStatus(TaskStatus.COMPLETED);
        task.setResultMinioObjectName(resultObjectKey);
        taskRepository.save(task);

        mockMvc.perform(get("/api/v1/tasks/{id}/download", taskId)
                        .header("Authorization", "Bearer " + otherUserAccessToken))
                .andExpect(status().isNotFound());
    }

    @Test
    void shouldReturnConflictWhenDownloadingNotCompletedTask() throws Exception {
        String taskId = createTask(userAccessToken);

        mockMvc.perform(get("/api/v1/tasks/{id}/download", taskId)
                        .header("Authorization", "Bearer " + userAccessToken))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.title").value("Task Not Completed"));
    }

    @Test
    void shouldReturnNotFoundWhenResultFileMissing() throws Exception {
        String taskId = createTask(userAccessToken);

        Task task = taskRepository.findById(UUID.fromString(taskId)).orElseThrow();
        task.setStatus(TaskStatus.COMPLETED);
        taskRepository.save(task);

        mockMvc.perform(get("/api/v1/tasks/{id}/download", taskId)
                        .header("Authorization", "Bearer " + userAccessToken))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.title").value("Result File Not Found"));
    }

    /* ==================== Безопасность ==================== */

    @Test
    void shouldDenyAccessWithoutJwt() throws Exception {
        mockMvc.perform(get("/api/v1/tasks"))
                .andExpect(status().isUnauthorized());
    }

    /* ==================== Вспомогательные методы ==================== */

    private String createTask(String accessToken) throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file", "test-document.pdf", MediaType.APPLICATION_PDF_VALUE, "Test PDF content".getBytes()
        );

        MvcResult result = mockMvc.perform(multipart("/api/v1/tasks")
                        .file(file)
                        .header("Authorization", "Bearer " + accessToken))
                .andExpect(status().isCreated())
                .andReturn();

        return objectMapper.readTree(result.getResponse().getContentAsString()).get("id").asText();
    }

    private String registerAndGetAccessToken(String username, String email) throws Exception {
        RegisterRequest request = new RegisterRequest(
                username, email, "securePassword123", "Test", "User"
        );

        MvcResult result = mockMvc.perform(post("/api/v1/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andReturn();

        LoginResponse loginResponse = objectMapper.readValue(
                result.getResponse().getContentAsString(), LoginResponse.class
        );

        return loginResponse.accessToken();
    }
}