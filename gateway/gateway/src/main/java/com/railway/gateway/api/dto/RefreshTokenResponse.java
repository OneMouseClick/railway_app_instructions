package com.railway.gateway.api.dto;

import io.swagger.v3.oas.annotations.media.Schema;

@Schema(description = "Refresh token response with new access token")
public record RefreshTokenResponse(
        @Schema(description = "New JWT access token")
        String accessToken,

        @Schema(description = "Access token expiration time in milliseconds", example = "900000")
        Long expiresIn,

        @Schema(description = "Token type", example = "Bearer")
        String tokenType
) {
    public RefreshTokenResponse(String accessToken, Long expiresIn) {
        this(accessToken, expiresIn, "Bearer");
    }
}