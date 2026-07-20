package com.railway.gateway.domain.exception;

import java.util.UUID;

public class UserNotFoundException extends RuntimeException {

    public UserNotFoundException(String message) {
        super(message);
    }

    public UserNotFoundException(UUID userId) {
        super("User not found with id: " + userId);
    }

    public UserNotFoundException(String username, boolean byUsername) {
        super("User not found with " + (byUsername ? "username: " : "email: ") + username);
    }
}