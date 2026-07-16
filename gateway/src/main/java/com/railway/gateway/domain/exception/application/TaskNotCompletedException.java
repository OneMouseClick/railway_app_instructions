package com.railway.gateway.domain.exception.application;

import com.railway.gateway.domain.enums.TaskStatus;

import java.util.UUID;

public class TaskNotCompletedException extends RuntimeException {

    public TaskNotCompletedException(UUID taskId, TaskStatus currentStatus) {
        super("Task with id: %s is not completed. Current status: %s".formatted(taskId, currentStatus));
    }
}