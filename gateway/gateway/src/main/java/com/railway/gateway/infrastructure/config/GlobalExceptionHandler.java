package com.railway.gateway.infrastructure.config;

import com.railway.gateway.api.dto.ErrorResponse;
import com.railway.gateway.domain.exception.RefreshTokenNotFoundException;
import com.railway.gateway.domain.exception.TaskNotFoundException;
import com.railway.gateway.domain.exception.UserNotFoundException;
import com.railway.gateway.domain.exception.application.EmailAlreadyExistsException;
import com.railway.gateway.domain.exception.application.FileValidationException;
import com.railway.gateway.domain.exception.application.InvalidCredentialsException;
import com.railway.gateway.domain.exception.application.InvalidTaskStatusException;
import com.railway.gateway.domain.exception.application.RefreshTokenExpiredException;
import com.railway.gateway.domain.exception.application.ResultFileNotFoundException;
import com.railway.gateway.domain.exception.application.TaskNotCompletedException;
import com.railway.gateway.domain.exception.application.TaskOperationException;
import com.railway.gateway.domain.exception.application.UsernameAlreadyExistsException;
import com.railway.gateway.domain.exception.infrastructure.BucketNotFoundException;
import com.railway.gateway.domain.exception.infrastructure.FileDownloadException;
import com.railway.gateway.domain.exception.infrastructure.FileUploadException;
import com.railway.gateway.domain.exception.infrastructure.ObjectNotFoundException;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.multipart.MaxUploadSizeExceededException;

import java.time.Instant;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(FileValidationException.class)
    public ResponseEntity<ErrorResponse> handleFileValidationException(
            FileValidationException ex, HttpServletRequest request) {
        log.warn("File validation error: {}", ex.getMessage());
        return buildErrorResponse(HttpStatus.BAD_REQUEST, "File Validation Error", ex.getMessage(), request);
    }

    @ExceptionHandler(MaxUploadSizeExceededException.class)
    public ResponseEntity<ErrorResponse> handleMaxUploadSizeExceededException(
            MaxUploadSizeExceededException ex, HttpServletRequest request) {
        log.warn("File size exceeds maximum allowed size");
        return buildErrorResponse(HttpStatus.PAYLOAD_TOO_LARGE, "File Too Large",
                "File size exceeds maximum allowed size of 100MB", request);
    }

    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFoundException(
            UserNotFoundException ex, HttpServletRequest request) {
        log.warn("User not found: {}", ex.getMessage());
        return buildErrorResponse(HttpStatus.NOT_FOUND, "User Not Found", ex.getMessage(), request);
    }

    @ExceptionHandler(TaskNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleTaskNotFoundException(
            TaskNotFoundException ex, HttpServletRequest request) {
        log.warn("Task not found: {}", ex.getMessage());
        return buildErrorResponse(HttpStatus.NOT_FOUND, "Task Not Found", ex.getMessage(), request);
    }

    @ExceptionHandler(ObjectNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleObjectNotFoundException(
            ObjectNotFoundException ex, HttpServletRequest request) {
        log.error("Object not found in MinIO: {}", ex.getMessage());
        return buildErrorResponse(HttpStatus.NOT_FOUND, "Object Not Found", ex.getMessage(), request);
    }

    @ExceptionHandler(BucketNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleBucketNotFoundException(
            BucketNotFoundException ex, HttpServletRequest request) {
        log.error("Bucket not found: {}", ex.getMessage());
        return buildErrorResponse(HttpStatus.INTERNAL_SERVER_ERROR, "Storage Error", ex.getMessage(), request);
    }

    @ExceptionHandler(FileUploadException.class)
    public ResponseEntity<ErrorResponse> handleFileUploadException(
            FileUploadException ex, HttpServletRequest request) {
        log.error("File upload failed: {}", ex.getMessage(), ex);
        return buildErrorResponse(HttpStatus.INTERNAL_SERVER_ERROR, "Upload Error", ex.getMessage(), request);
    }

    @ExceptionHandler(FileDownloadException.class)
    public ResponseEntity<ErrorResponse> handleFileDownloadException(
            FileDownloadException ex, HttpServletRequest request) {
        log.error("File download failed: {}", ex.getMessage(), ex);
        return buildErrorResponse(HttpStatus.INTERNAL_SERVER_ERROR, "Download Error", ex.getMessage(), request);
    }

    @ExceptionHandler(TaskOperationException.class)
    public ResponseEntity<ErrorResponse> handleTaskOperationException(
            TaskOperationException ex, HttpServletRequest request) {
        log.error("Task operation failed: {}", ex.getMessage(), ex);
        return buildErrorResponse(HttpStatus.INTERNAL_SERVER_ERROR, "Task Operation Error", ex.getMessage(), request);
    }

    @ExceptionHandler(UsernameAlreadyExistsException.class)
    public ResponseEntity<ErrorResponse> handleUsernameAlreadyExistsException(
            UsernameAlreadyExistsException ex, HttpServletRequest request) {
        log.warn("Username already exists: {}", ex.getMessage());
        return buildErrorResponse(HttpStatus.CONFLICT, "Username Already Exists", ex.getMessage(), request);
    }

    @ExceptionHandler(EmailAlreadyExistsException.class)
    public ResponseEntity<ErrorResponse> handleEmailAlreadyExistsException(
            EmailAlreadyExistsException ex, HttpServletRequest request) {
        log.warn("Email already exists: {}", ex.getMessage());
        return buildErrorResponse(HttpStatus.CONFLICT, "Email Already Exists", ex.getMessage(), request);
    }

    @ExceptionHandler(InvalidCredentialsException.class)
    public ResponseEntity<ErrorResponse> handleInvalidCredentialsException(
            InvalidCredentialsException ex, HttpServletRequest request) {
        log.warn("Invalid credentials: {}", ex.getMessage());
        return buildErrorResponse(HttpStatus.UNAUTHORIZED, "Invalid Credentials", ex.getMessage(), request);
    }

    @ExceptionHandler(RefreshTokenExpiredException.class)
    public ResponseEntity<ErrorResponse> handleRefreshTokenExpiredException(
            RefreshTokenExpiredException ex, HttpServletRequest request) {
        log.warn("Refresh token expired: {}", ex.getMessage());
        return buildErrorResponse(HttpStatus.UNAUTHORIZED, "Token Expired", ex.getMessage(), request);
    }

    @ExceptionHandler(RefreshTokenNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleRefreshTokenNotFoundException(
            RefreshTokenNotFoundException ex, HttpServletRequest request) {
        log.warn("Refresh token not found: {}", ex.getMessage());
        return buildErrorResponse(HttpStatus.UNAUTHORIZED, "Invalid Token", ex.getMessage(), request);
    }

    @ExceptionHandler(TaskNotCompletedException.class)
    public ResponseEntity<ErrorResponse> handleTaskNotCompletedException(
            TaskNotCompletedException ex, HttpServletRequest request) {
        log.warn("Task not completed: {}", ex.getMessage());
        return buildErrorResponse(HttpStatus.CONFLICT, "Task Not Completed", ex.getMessage(), request);
    }

    @ExceptionHandler(ResultFileNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleResultFileNotFoundException(
            ResultFileNotFoundException ex, HttpServletRequest request) {
        log.warn("Result file not found: {}", ex.getMessage());
        return buildErrorResponse(HttpStatus.NOT_FOUND, "Result File Not Found", ex.getMessage(), request);
    }

    @ExceptionHandler(InvalidTaskStatusException.class)
    public ResponseEntity<ErrorResponse> handleInvalidTaskStatusException(
            InvalidTaskStatusException ex, HttpServletRequest request) {
        log.warn("Invalid task status: {}", ex.getMessage());
        return buildErrorResponse(HttpStatus.BAD_REQUEST, "Invalid Status", ex.getMessage(), request);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGenericException(
            Exception ex, HttpServletRequest request) {
        log.error("Unexpected error: {}", ex.getMessage(), ex);
        return buildErrorResponse(HttpStatus.INTERNAL_SERVER_ERROR, "Internal Server Error",
                "An unexpected error occurred. Please try again later.", request);
    }

    private ResponseEntity<ErrorResponse> buildErrorResponse(
            HttpStatus status, String title, String detail, HttpServletRequest request) {
        ErrorResponse errorResponse = new ErrorResponse(
                status.value(),
                title,
                detail,
                Instant.now(),
                request.getRequestURI(),
                null
        );
        return ResponseEntity.status(status)
                .contentType(MediaType.APPLICATION_JSON)
                .body(errorResponse);
    }
}