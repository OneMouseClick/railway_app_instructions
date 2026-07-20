package com.railway.gateway.application.validator;

import com.railway.gateway.domain.exception.application.FileValidationException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

import java.util.Set;

@Slf4j
@Component
public class FileValidator {

    private static final long MAX_FILE_SIZE = 100 * 1024 * 1024;
    private static final Set<String> ALLOWED_EXTENSIONS = Set.of(
            "pdf", "docx", "doc", "png", "jpg", "jpeg"
    );

    public void validate(MultipartFile file) {
        if (file == null) {
            throw new FileValidationException("File must not be null");
        }

        if (file.isEmpty()) {
            throw new FileValidationException("File must not be empty");
        }

        if (file.getSize() > MAX_FILE_SIZE) {
            throw new FileValidationException(
                    "File size exceeds maximum allowed size of %d MB".formatted(MAX_FILE_SIZE / (1024 * 1024))
            );
        }

        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null || originalFilename.isBlank()) {
            throw new FileValidationException("File name must not be blank");
        }

        String extension = getFileExtension(originalFilename);
        if (extension.isEmpty() || !ALLOWED_EXTENSIONS.contains(extension)) {
            throw new FileValidationException(
                    "Unsupported file extension: '%s'. Allowed extensions: %s"
                            .formatted(extension, String.join(", ", ALLOWED_EXTENSIONS))
            );
        }

        String contentType = file.getContentType();
        if (contentType == null) {
            throw new FileValidationException("File content type must not be null");
        }

        log.debug("File validation passed: name={}, size={}, extension={}, contentType={}",
                originalFilename, file.getSize(), extension, contentType);
    }

    public static String getFileExtension(String fileName) {
        if (fileName == null || fileName.isEmpty()) {
            return "";
        }
        int lastDotIndex = fileName.lastIndexOf('.');
        if (lastDotIndex == -1 || lastDotIndex == fileName.length() - 1) {
            return "";
        }
        return fileName.substring(lastDotIndex + 1).toLowerCase();
    }
}