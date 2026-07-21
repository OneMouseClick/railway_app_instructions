package com.railway.gateway.api.controller;

import com.railway.gateway.api.dto.CreateTaskResponse;
import com.railway.gateway.api.dto.ErrorResponse;
import com.railway.gateway.api.dto.TaskContentRequest;
import com.railway.gateway.api.dto.TaskContentResponse;
import com.railway.gateway.api.dto.TaskDetailsResponse;
import com.railway.gateway.api.dto.TaskPageResponse;
import com.railway.gateway.api.dto.TaskStatusResponse;
import com.railway.gateway.application.service.TaskService;
import com.railway.gateway.domain.enums.TaskStatus;
import com.railway.gateway.domain.exception.application.InvalidTaskStatusException;
import com.railway.gateway.infrastructure.security.SecurityUser;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.enums.ParameterIn;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDateTime;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/tasks")
@RequiredArgsConstructor
@Tag(name = "Task Management", description = "API for managing document processing tasks")
@SecurityRequirement(name = "Bearer Authentication")
public class TaskController {

    private final TaskService taskService;

    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create a new task", description = "Upload a document and create a new processing task")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "201", description = "Task created successfully",
                    content = @Content(schema = @Schema(implementation = CreateTaskResponse.class))),
            @ApiResponse(responseCode = "400", description = "Invalid file",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))),
            @ApiResponse(responseCode = "401", description = "Unauthorized",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class)))
    })
    public CreateTaskResponse createTask(
            @AuthenticationPrincipal SecurityUser securityUser,
            @Parameter(description = "Document file to process", required = true)
            @RequestParam("file") MultipartFile file) {
        return taskService.createTask(securityUser.getId(), file);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get task details",
            description = "Retrieve detailed information about a task. Returns 404 if task belongs to another user.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Task found",
                    content = @Content(schema = @Schema(implementation = TaskDetailsResponse.class))),
            @ApiResponse(responseCode = "401", description = "Unauthorized",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))),
            @ApiResponse(responseCode = "404", description = "Task not found",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class)))
    })
    public TaskDetailsResponse getTask(
            @AuthenticationPrincipal SecurityUser securityUser,
            @Parameter(description = "Task ID", required = true, example = "550e8400-e29b-41d4-a716-446655440000", in = ParameterIn.PATH)
            @PathVariable("id") UUID id) {
        return taskService.getTask(securityUser.getId(), id);
    }

    @GetMapping
    @Operation(summary = "Get user tasks",
            description = "Retrieve paginated and filtered list of user's tasks. Supports filtering by status and date range.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Tasks retrieved successfully",
                    content = @Content(schema = @Schema(implementation = TaskPageResponse.class))),
            @ApiResponse(responseCode = "400", description = "Invalid filter parameters",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))),
            @ApiResponse(responseCode = "401", description = "Unauthorized",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class)))
    })
    public TaskPageResponse getTasks(
            @AuthenticationPrincipal SecurityUser securityUser,
            @Parameter(description = "Page number (0-based)", example = "0")
            @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Page size", example = "10")
            @RequestParam(defaultValue = "10") int size,
            @Parameter(description = "Sort field and direction (e.g., 'createdAt,desc')", example = "createdAt,desc")
            @RequestParam(required = false) String sort,
            @Parameter(description = "Filter by task status", example = "COMPLETED")
            @RequestParam(required = false) String status,
            @Parameter(description = "Filter tasks created after this date-time (ISO 8601)", example = "2026-07-01T00:00:00")
            @RequestParam(required = false) LocalDateTime createdFrom,
            @Parameter(description = "Filter tasks created before this date-time (ISO 8601)", example = "2026-07-31T23:59:59")
            @RequestParam(required = false) LocalDateTime createdTo) {

        TaskStatus taskStatus = null;
        if (status != null && !status.isBlank()) {
            try {
                taskStatus = TaskStatus.valueOf(status.toUpperCase());
            } catch (IllegalArgumentException e) {
                throw new InvalidTaskStatusException(status);
            }
        }

        return taskService.getTasks(securityUser.getId(), page, size, sort, taskStatus, createdFrom, createdTo);
    }

    @GetMapping("/{id}/status")
    @Operation(summary = "Get task status", description = "Retrieve only the status of a task")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Task status retrieved",
                    content = @Content(schema = @Schema(implementation = TaskStatusResponse.class))),
            @ApiResponse(responseCode = "401", description = "Unauthorized",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))),
            @ApiResponse(responseCode = "404", description = "Task not found",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class)))
    })
    public TaskStatusResponse getTaskStatus(
            @AuthenticationPrincipal SecurityUser securityUser,
            @Parameter(description = "Task ID", required = true, example = "550e8400-e29b-41d4-a716-446655440000", in = ParameterIn.PATH)
            @PathVariable("id") UUID id) {
        return taskService.getTaskStatus(securityUser.getId(), id);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    @Operation(summary = "Delete task", description = "Delete a task and its associated files")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "204", description = "Task deleted successfully"),
            @ApiResponse(responseCode = "401", description = "Unauthorized",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))),
            @ApiResponse(responseCode = "404", description = "Task not found",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class)))
    })
    public void deleteTask(
            @AuthenticationPrincipal SecurityUser securityUser,
            @Parameter(description = "Task ID", required = true, example = "550e8400-e29b-41d4-a716-446655440000", in = ParameterIn.PATH)
            @PathVariable("id") UUID id) {
        taskService.deleteTask(securityUser.getId(), id);
    }

    @GetMapping("/{id}/download")
    @Operation(summary = "Download generated instruction PDF",
            description = "Download the final generated instruction as a PDF file. Task must be in COMPLETED status.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "PDF file downloaded successfully",
                    content = @Content(mediaType = MediaType.APPLICATION_PDF_VALUE)),
            @ApiResponse(responseCode = "401", description = "Unauthorized",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))),
            @ApiResponse(responseCode = "404", description = "Task not found or result file not found",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))),
            @ApiResponse(responseCode = "409", description = "Task is not completed yet",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))),
            @ApiResponse(responseCode = "500", description = "Internal server error",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class)))
    })
    public ResponseEntity<Resource> downloadTask(
            @AuthenticationPrincipal SecurityUser securityUser,
            @Parameter(description = "Task ID", required = true, example = "550e8400-e29b-41d4-a716-446655440000", in = ParameterIn.PATH)
            @PathVariable("id") UUID id) {

        Resource resource = taskService.downloadTask(securityUser.getId(), id);

        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_PDF)
                .header(HttpHeaders.CONTENT_DISPOSITION,
                        "attachment; filename=\"station-instruction.pdf\"")
                .body(resource);
    }

    @GetMapping("/{id}/content")
    @Operation(summary = "Get generated instruction text",
            description = "Returns plain-text instruction assembled from generated-json in MinIO.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Content loaded",
                    content = @Content(schema = @Schema(implementation = TaskContentResponse.class))),
            @ApiResponse(responseCode = "401", description = "Unauthorized",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))),
            @ApiResponse(responseCode = "404", description = "Task or generated JSON not found",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))),
            @ApiResponse(responseCode = "409", description = "Instruction is not generated yet",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class)))
    })
    public TaskContentResponse getTaskContent(
            @AuthenticationPrincipal SecurityUser securityUser,
            @PathVariable("id") UUID id) {
        return taskService.getTaskContent(securityUser.getId(), id);
    }

    @PutMapping(value = "/{id}/content", consumes = MediaType.APPLICATION_JSON_VALUE)
    @Operation(summary = "Save edited instruction text",
            description = "Updates generated-json in MinIO. Does not rebuild PDF automatically.")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Content saved",
                    content = @Content(schema = @Schema(implementation = TaskContentResponse.class))),
            @ApiResponse(responseCode = "401", description = "Unauthorized",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))),
            @ApiResponse(responseCode = "404", description = "Task or generated JSON not found",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class))),
            @ApiResponse(responseCode = "409", description = "Instruction is not generated yet",
                    content = @Content(schema = @Schema(implementation = ErrorResponse.class)))
    })
    public TaskContentResponse saveTaskContent(
            @AuthenticationPrincipal SecurityUser securityUser,
            @PathVariable("id") UUID id,
            @Valid @RequestBody TaskContentRequest request) {
        return taskService.saveTaskContent(securityUser.getId(), id, request);
    }
}