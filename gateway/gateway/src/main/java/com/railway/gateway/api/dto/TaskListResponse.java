package com.railway.gateway.api.dto;

import io.swagger.v3.oas.annotations.media.Schema;

import java.util.List;

@Schema(description = "Paginated list of tasks")
public record TaskListResponse(
        @Schema(description = "List of tasks")
        List<TaskResponse> tasks,

        @Schema(description = "Total number of tasks", example = "42")
        long totalElements,

        @Schema(description = "Total number of pages", example = "5")
        int totalPages,

        @Schema(description = "Current page number (0-based)", example = "0")
        int currentPage,

        @Schema(description = "Page size", example = "10")
        int pageSize
) {
}