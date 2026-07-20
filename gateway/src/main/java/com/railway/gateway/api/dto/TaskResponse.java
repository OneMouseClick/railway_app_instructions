package com.railway.gateway.api.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDateTime;
import java.util.UUID;

@Schema(description = "Full task information")
public record TaskResponse(
        @Schema(description = "Task unique identifier", example = "550e8400-e29b-41d4-a716-446655440000")
        UUID id,

        @Schema(description = "Task status", example = "CREATED")
        String status,

        @Schema(description = "Original file name", example = "station-schema.pdf")
        String originalFileName,

        @Schema(description = "Original file type", example = "application/pdf")
        String originalFileType,

        @Schema(description = "Error message if task failed")
        String errorMessage,

        @Schema(description = "Task creation timestamp")
        LocalDateTime createdAt,

        @Schema(description = "Task last update timestamp")
        LocalDateTime updatedAt
) {
}