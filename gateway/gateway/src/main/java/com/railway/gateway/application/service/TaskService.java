package com.railway.gateway.application.service;

import com.railway.gateway.api.dto.CreateTaskResponse;
import com.railway.gateway.api.dto.TaskContentRequest;
import com.railway.gateway.api.dto.TaskContentResponse;
import com.railway.gateway.api.dto.TaskDetailsResponse;
import com.railway.gateway.api.dto.TaskPageResponse;
import com.railway.gateway.api.dto.TaskStatusResponse;
import com.railway.gateway.domain.enums.TaskStatus;
import org.springframework.core.io.Resource;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDateTime;
import java.util.UUID;

public interface TaskService {

    CreateTaskResponse createTask(UUID userId, MultipartFile file);

    TaskDetailsResponse getTask(UUID userId, UUID taskId);

    TaskPageResponse getTasks(UUID userId, int page, int size, String sort, TaskStatus status,
                              LocalDateTime createdFrom, LocalDateTime createdTo);

    TaskStatusResponse getTaskStatus(UUID userId, UUID taskId);

    void deleteTask(UUID userId, UUID taskId);

    Resource downloadTask(UUID userId, UUID taskId);

    TaskContentResponse getTaskContent(UUID userId, UUID taskId);

    TaskContentResponse saveTaskContent(UUID userId, UUID taskId, TaskContentRequest request);

    void updateStatusToParsing(UUID taskId);

    void markParsed(UUID taskId, String parsedContentObjectKey);

    void updateStatusToGenerating(UUID taskId);

    void markGenerated(UUID taskId, String generatedInstructionObjectKey);

    void updateStatusToAssembling(UUID taskId);

    void markCompleted(UUID taskId, String resultMinioObjectName);

    void markFailed(UUID taskId, String errorMessage);
}