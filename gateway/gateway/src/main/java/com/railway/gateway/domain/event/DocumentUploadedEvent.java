package com.railway.gateway.domain.event;

import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

import java.util.UUID;

@Data
@SuperBuilder
@NoArgsConstructor
@EqualsAndHashCode(callSuper = true)
public class DocumentUploadedEvent extends BaseEvent {

    private UUID userId;
    private String originalFileName;
    private String minioObjectKey;

    public DocumentUploadedEvent(UUID taskId, UUID userId, String originalFileName, String minioObjectKey) {
        super("DOCUMENT_UPLOADED");
        this.taskId = taskId;
        this.correlationId = taskId;
        this.userId = userId;
        this.originalFileName = originalFileName;
        this.minioObjectKey = minioObjectKey;
    }
}