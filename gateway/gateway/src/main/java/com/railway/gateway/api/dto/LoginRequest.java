package com.railway.gateway.api.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;

@Schema(description = "Login request payload")
public record LoginRequest(
        @Schema(description = "Username", example = "testuser")
        @NotBlank(message = "Username must not be blank")
        String username,

        @Schema(description = "Password", example = "securePassword123")
        @NotBlank(message = "Password must not be blank")
        String password
) {
}