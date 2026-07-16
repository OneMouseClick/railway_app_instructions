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
public class CompletedEvent extends BaseEvent {

    private String resultMinioObjectName;

    public CompletedEvent(UUID taskId, String resultMinioObjectName) {
        super("COMPLETED");
        this.taskId = taskId;
        this.correlationId = taskId;
        this.resultMinioObjectName = resultMinioObjectName;
    }
}