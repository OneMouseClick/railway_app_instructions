package com.railway.gateway.domain.exception;

import java.util.UUID;

public class TaskNotFoundException extends RuntimeException {

    public TaskNotFoundException(String message) {
        super(message);
    }

    public TaskNotFoundException(UUID taskId) {
        super("Task not found with id: " + taskId);
    }

    public TaskNotFoundException(UUID taskId, UUID userId) {
        super("Task not found with id: " + taskId + " for user: " + userId);
    }
}