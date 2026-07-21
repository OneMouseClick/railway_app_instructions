package com.railway.gateway.api.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;

@Schema(description = "Updated instruction text from the browser editor")
public record TaskContentRequest(
        @NotBlank
        @Schema(description = "Full instruction text")
        String content
) {
}
