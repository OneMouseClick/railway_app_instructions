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
public class FailedEvent extends BaseEvent {

    private String errorMessage;

    public FailedEvent(UUID taskId, String errorMessage) {
        super("FAILED");
        this.taskId = taskId;
        this.correlationId = taskId;
        this.errorMessage = errorMessage;
    }
}