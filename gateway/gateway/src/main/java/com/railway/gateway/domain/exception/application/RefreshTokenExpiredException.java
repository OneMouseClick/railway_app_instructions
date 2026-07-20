package com.railway.gateway.domain.exception.application;

public class RefreshTokenExpiredException extends RuntimeException {

    public RefreshTokenExpiredException() {
        super("Refresh token has expired");
    }

    public RefreshTokenExpiredException(String message) {
        super(message);
    }
}