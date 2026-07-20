package com.railway.gateway.domain.exception.application;

import java.util.UUID;

public class TaskOperationException extends RuntimeException {

    public TaskOperationException(String message) {
        super(message);
    }

    public TaskOperationException(String message, Throwable cause) {
        super(message, cause);
    }

    public TaskOperationException(UUID taskId, String operation) {
        super("Failed to %s task with id: %s".formatted(operation, taskId));
    }

    public TaskOperationException(UUID taskId, String operation, Throwable cause) {
        super("Failed to %s task with id: %s".formatted(operation, taskId), cause);
    }
}