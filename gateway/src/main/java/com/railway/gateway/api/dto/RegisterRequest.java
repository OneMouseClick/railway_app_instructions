package com.railway.gateway.api.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

@Schema(description = "User registration request payload")
public record RegisterRequest(
        @Schema(description = "Username", example = "testuser")
        @NotBlank(message = "Username must not be blank")
        @Size(min = 3, max = 100, message = "Username must be between 3 and 100 characters")
        String username,

        @Schema(description = "Email address", example = "testuser@railway.com")
        @NotBlank(message = "Email must not be blank")
        @Email(message = "Email must be valid")
        String email,

        @Schema(description = "Password", example = "securePassword123")
        @NotBlank(message = "Password must not be blank")
        @Size(min = 8, max = 100, message = "Password must be between 8 and 100 characters")
        String password,

        @Schema(description = "First name", example = "Test")
        @Size(max = 100, message = "First name must be at most 100 characters")
        String firstName,

        @Schema(description = "Last name", example = "User")
        @Size(max = 100, message = "Last name must be at most 100 characters")
        String lastName
) {
}