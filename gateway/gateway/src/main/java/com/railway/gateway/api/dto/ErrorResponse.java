package com.railway.gateway.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.Instant;
import java.util.List;

@JsonInclude(JsonInclude.Include.NON_NULL)
@Schema(description = "Standard error response")
public record ErrorResponse(
        @Schema(description = "HTTP status code", example = "400")
        int status,

        @Schema(description = "Error type", example = "Bad Request")
        String title,

        @Schema(description = "Detailed error message", example = "File size exceeds maximum allowed size of 100MB")
        String detail,

        @Schema(description = "Error timestamp")
        Instant timestamp,

        @Schema(description = "Request path", example = "/api/v1/tasks")
        String path,

        @Schema(description = "Validation errors list")
        List<ValidationError> errors
) {
    @Schema(description = "Single validation error")
    public record ValidationError(
            @Schema(description = "Field name", example = "file")
            String field,

            @Schema(description = "Error message", example = "File is empty")
            String message
    ) {
    }
}