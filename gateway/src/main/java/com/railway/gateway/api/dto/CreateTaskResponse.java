package com.railway.gateway.api.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDateTime;
import java.util.UUID;

@Schema(description = "Response after task creation")
public record CreateTaskResponse(
        @Schema(description = "Task unique identifier", example = "550e8400-e29b-41d4-a716-446655440000")
        UUID id,

        @Schema(description = "Task status", example = "CREATED")
        String status,

        @Schema(description = "Original file name", example = "station-schema.pdf")
        String originalFileName,

        @Schema(description = "Task creation timestamp")
        LocalDateTime createdAt
) {
}