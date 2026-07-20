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
public class TaskCreatedEvent extends BaseEvent {

    private UUID userId;
    private String originalFileName;
    private String minioObjectKey;

    public TaskCreatedEvent(UUID taskId, UUID userId, String originalFileName, String minioObjectKey) {
        super("TASK_CREATED");
        this.taskId = taskId;
        this.correlationId = taskId;
        this.userId = userId;
        this.originalFileName = originalFileName;
        this.minioObjectKey = minioObjectKey;
    }
}