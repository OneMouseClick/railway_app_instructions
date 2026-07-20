package com.railway.gateway.domain.exception;

import java.util.UUID;

public class RefreshTokenNotFoundException extends RuntimeException {

    public RefreshTokenNotFoundException(String message) {
        super(message);
    }

    public RefreshTokenNotFoundException(UUID tokenId) {
        super("Refresh token not found with id: " + tokenId);
    }

    public RefreshTokenNotFoundException(String token, boolean byToken) {
        super("Refresh token not found: " + token);
    }
}