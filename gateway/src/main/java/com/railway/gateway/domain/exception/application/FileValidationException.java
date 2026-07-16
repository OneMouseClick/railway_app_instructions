package com.railway.gateway.domain.exception.application;

public class FileValidationException extends RuntimeException {

    public FileValidationException(String message) {
        super(message);
    }
}