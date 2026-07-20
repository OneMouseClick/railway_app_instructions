package com.railway.gateway.api.dto;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "Login response with JWT tokens")
public record LoginResponse(
        @Schema(description = "JWT access token")
        String accessToken,

        @Schema(description = "Refresh token")
        String refreshToken,

        @Schema(description = "Access token expiration time in milliseconds", example = "900000")
        Long expiresIn,

        @Schema(description = "Token type", example = "Bearer")
        String tokenType
) {
    public LoginResponse(String accessToken, String refreshToken, Long expiresIn) {
        this(accessToken, refreshToken, expiresIn, "Bearer");
    }
}