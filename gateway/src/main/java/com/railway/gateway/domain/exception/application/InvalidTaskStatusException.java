package com.railway.gateway.domain.exception.application;

public class InvalidTaskStatusException extends RuntimeException {

    public InvalidTaskStatusException(String status) {
        super("Invalid task status: " + status);
    }
}