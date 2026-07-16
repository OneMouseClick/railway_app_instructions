package com.railway.gateway.domain.exception.application;

import java.util.UUID;

public class ResultFileNotFoundException extends RuntimeException {

    public ResultFileNotFoundException(UUID taskId) {
        super("Result file not found for task with id: " + taskId);
    }

    public ResultFileNotFoundException(UUID taskId, Throwable cause) {
        super("Result file not found for task with id: " + taskId, cause);
    }
}